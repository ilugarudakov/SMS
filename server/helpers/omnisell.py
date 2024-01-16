from ..models import CollectorModels, OmnicellModel, db
from typing import List, Any, Optional
from ..requests import OmnisellRequest
from requests import Response
from datetime import datetime, timedelta
from config import Config
from sqlalchemy import or_, create_engine
from sqlalchemy.orm import Session
from .response_patch import MyResponse
from logger import logger


class OmnisellTask:

    def __init__(self):
        self.engine = create_engine(Config.DATABASE.SQLALCHEMY_DATABASE_URI)
        self.session = Session(bind=self.engine)

    def get_new_messages(self) -> Optional[List[CollectorModels.collector]]:
        try:
            return self.session.query(CollectorModels.collector).filter_by(status='INITIAL').all()
        except Exception as e:
            logger.error(f'Some DB error: {e}')
            return None

    def update_message_statuses(self, messages: List[CollectorModels.collector]) -> None:
        if isinstance(messages, list):
            for i in messages:
                i.status = 'PROCESSED'
                i.last_modified = datetime.now()
                try:
                    self.session.add(i)
                except Exception as err:
                    logger.error(f'Cant update message statuses:', {err})
            self.session.commit()

    def chek_ttl(self) -> None:
        initial_tasks = self.get_inintial_tasks()
        if initial_tasks:
            now = datetime.now()
            for initial_task in initial_tasks:
                seconds = (now - initial_task.last_modified).total_seconds()
                if seconds > Config.TTL:
                    initial_task.status = OmnicellModel.enums.statuses.EXPIRED
                    self.session.add(initial_task)
        expired_groups = self.get_expired_groups()
        for group in expired_groups:
            logger.warning(f'group ids must be canceled: {group.group_id}')
            group.status = OmnicellModel.enums.group_id_statuses.CANCELED
        try:
            self.session.commit()
            logger.warning(f'updating group id statuses')
        except Exception as err:
            self.session.rollback()
            logger.error(f'Can not chek_ttl {err}')

    def get_all_tasks(self, param: str) -> List[OmnicellModel.omnicell_tasks]:
        return self.session.query(
            OmnicellModel.omnicell_tasks
        ).filter(or_(
            OmnicellModel.omnicell_tasks.message.has(account=param),
            OmnicellModel.omnicell_tasks.message.has(phone=param)
        )).order_by(
            OmnicellModel.omnicell_tasks.last_modified.desc()
        ).limit(20).all()

    def get_all_tasks_last_day(self) -> List[OmnicellModel.omnicell_tasks]:
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tasks = self.session.query(
            OmnicellModel.omnicell_tasks
        ).filter(
            OmnicellModel.omnicell_tasks.last_modified > yesterday
        ).all()
        return tasks

    def get_inintial_tasks(self) -> list:
        tasks = self.session.query(OmnicellModel.omnicell_tasks)
        tasks = tasks.filter_by(status=CollectorModels.statuses.INITIAL.value).all()
        return tasks

    def get_expired_groups(self) -> list:
        return self.session.query(
            OmnicellModel.group_ids
        ).join(
            OmnicellModel.omnicell_tasks,
            OmnicellModel.omnicell_tasks.group_id == OmnicellModel.group_ids.group_id
        ).filter(
            OmnicellModel.omnicell_tasks.delivery_date == None,
            OmnicellModel.group_ids.status == OmnicellModel.enums.group_id_statuses.INITIAL.value,
            OmnicellModel.omnicell_tasks.last_modified < datetime.now() - timedelta(days=2)
        ).group_by(
            OmnicellModel.group_ids.group_id,
            OmnicellModel.omnicell_tasks.last_modified,
            OmnicellModel.omnicell_tasks.delivery_date
        ).all()


    def make_mailing(self, messages: List[CollectorModels.collector]) -> None:
        for message in messages:
            mailing = OmnicellModel.omnicell_tasks()
            if len(messages) == 1:
                mailing.mailing_list_type = OmnicellModel.enums.mailing_list_types.SINGLE.value
            else:
                mailing.mailing_list_type = OmnicellModel.enums.mailing_list_types.INDIVIDUAL.value
            mailing.message_id = message.id
            self.session.add(mailing)
            message.status = CollectorModels.statuses.PROCESSED.value
        try:
            self.session.commit()
        except Exception as err:
            self.session.rollback()
            logger.error(f'Can not make_mailing {err}')

    def get_individual_tasks(self) -> List[OmnicellModel.omnicell_tasks]:
        tasks = self.session.query(OmnicellModel.omnicell_tasks)
        tasks = tasks.filter_by(status=CollectorModels.statuses.INITIAL.value)
        tasks = tasks.filter_by(mailing_list_type=OmnicellModel.enums.mailing_list_types.INDIVIDUAL.value).all()
        return tasks

    def get_single_tasks(self) -> list[tuple[Any]]:
        tasks = self.session.query(OmnicellModel.omnicell_tasks)
        tasks = tasks.filter_by(status=CollectorModels.statuses.INITIAL.value)
        tasks = tasks.filter_by(mailing_list_type=OmnicellModel.enums.mailing_list_types.SINGLE.value).all()
        return tasks

    def update_tasks(self, response: Response, tasks: List[OmnicellModel.omnicell_tasks]) -> None:
        if response:
            prepared_response = MyResponse(**response.json())
            idx = 0
            if prepared_response.groupid:
                groupid = OmnicellModel.group_ids()
                groupid.group_id = prepared_response.groupid
                self.session.add(groupid)
            for task in tasks:
                task.remote_message_id = prepared_response.detail[idx].id
                task.status = prepared_response.detail[idx].state.value
                task.last_modified = datetime.now()
                if prepared_response.groupid:
                    task.group_id = prepared_response.groupid
                else:  # при отправке 1 сообщения лайф не возвращает груп ИД
                    task.mailing_list_type = OmnicellModel.enums.mailing_list_types.SINGLE.value
                idx += 1
                self.session.add(task)
            try:
                self.session.commit()
            except Exception as err:
                self.session.rollback()
                logger.error(f'Can not get_single_task {err}')

    def update_individual_accepted_tasks(self) -> None:
        groups = self.session.query(OmnicellModel.group_ids)
        groups = groups.filter_by(status=OmnicellModel.enums.group_id_statuses.INITIAL.value).all()
        a_tasks = self.session.query(OmnicellModel.omnicell_tasks)
        a_tasks = a_tasks.filter_by(status=OmnicellModel.enums.statuses.ACCEPTED.value)
        a_tasks = a_tasks.filter_by(mailing_list_type=OmnicellModel.enums.mailing_list_types.INDIVIDUAL.value).all()
        resps = []
        p_resps = []
        idx = 0
        if groups:  # если вдруг окажется несколько необработанных групп, обрабатываю в цикле.
            logger.debug('Have some initial groups. Lets check statuses')
            for group in groups:
                resps.append(OmnisellRequest().get_accepted_statuses(group.group_id))
                p_resps.append(MyResponse.parse_obj(resps[idx].json()))
                if p_resps[idx].reports == 'completed':
                    group.status = OmnicellModel.enums.group_id_statuses.DONE.value
                    self.session.add(group)
                idx += 1

            for p_resp in p_resps:
                if p_resp.reports == 'completed':
                    for det in p_resp.detail:
                        for a_task in a_tasks:
                            if str(det.id) == str(a_task.remote_message_id):
                                a_task.status = OmnicellModel.enums.statuses.DELIVERED.value
                                a_task.delivery_date = det.deliveryDate
                                a_task.last_modified = datetime.now()
                                self.session.add(a_task)
                try:
                    self.session.commit()
                except Exception as err:
                    self.session.rollback()
                    logger.error(f'Can not update_individual_accepted_tasks {err}')

    def update_single_accepted_tasks(self) -> None:
        sa_tasks = self.session.query(OmnicellModel.omnicell_tasks)
        sa_tasks = sa_tasks.filter_by(status=OmnicellModel.enums.statuses.ACCEPTED.value)
        sa_tasks = sa_tasks.filter_by(mailing_list_type=OmnicellModel.enums.mailing_list_types.SINGLE.value)
        sa_tasks = sa_tasks.all()
        resps = []
        p_resps = []
        idx = 0
        for sa_task in sa_tasks:
            resps.append(OmnisellRequest().get_single_accepted_statuses(sa_task.remote_message_id))
            p_resps.append(MyResponse.parse_obj(resps[idx].json()))
            sa_task.status = p_resps[idx].state.value
            sa_task.last_modified = datetime.now()
            if p_resps[idx].deliveryDate:
                sa_task.delivery_date = p_resps[idx].deliveryDate
            self.session.add(sa_task)
            idx += 1
        try:
            self.session.commit()
        except Exception as err:
            self.session.rollback()
            logger.error(f'Can not update_single_accepted_tasks {err}')


class OmnisellMessage:
    @staticmethod
    def add_to_db(account: int, phone: str, text: str) -> None:
        my_db_session = Session(bind=create_engine(Config.DATABASE.SQLALCHEMY_DATABASE_URI, pool_recycle = 3600, pool_pre_ping = True))
        if account and phone and text:
            message = CollectorModels.collector(
                account=account,
                phone=phone,
                text=text
            )
            try:
                my_db_session.add(message)
                my_db_session.commit()
            except Exception as err:
                my_db_session.rollback()
                logger.error(f'Can not add message to collector {err}')
            finally: my_db_session.close()
