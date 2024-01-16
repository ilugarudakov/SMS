from pydantic import BaseModel, root_validator
from datetime import datetime, timedelta
from pytz import timezone
from typing import List, Optional
from logger import logger


class MessageState(BaseModel):
    value: str


class MessageElem(BaseModel):
    id: int
    state: MessageState
    deliveryDate: Optional[datetime] = None

    @root_validator(allow_reuse=True)
    def check_time(cls, values: dict):
        deliv_date = values.get('deliveryDate', None)
        if deliv_date:
            correct_time = DateChanger.make_correct_date(deliv_date)
            values.update(deliveryDate=correct_time)
        return values


class MyResponse(BaseModel):
    deliveryDate: Optional[datetime] = None
    detail: Optional[List[MessageElem]] = []
    state: Optional[MessageState] = None
    id: Optional[int] = None
    groupid: Optional[int] = None
    reports: Optional[str] = None

    # для единичного сообщения ответ отличается. Добавим пару палей чтоб возвращать одинаковую структуру.
    @root_validator(allow_reuse=True)
    def check_order_id(cls, values: dict):
        if not values.get('detail', None):
            state = values.get('state', None)
            my_id = values.get('id', None)
            if state and my_id:
                elem = MessageElem(id=my_id, state=state)
                values.update({'detail': [elem]})

        deliv_date = values.get('deliveryDate', None)
        if deliv_date:
            correct_time = DateChanger.make_correct_date(deliv_date)
            values.update(deliveryDate=correct_time)
        return values


class DateChanger:
    @staticmethod
    def make_correct_date(deliv_date):
        if deliv_date:
            try:
                now = datetime.now(timezone('Europe/Kiev'))
                offset = now.utcoffset().total_seconds() / 3600
                return deliv_date + timedelta(hours=offset)
            except Exception as err:
                logger.warning(f'Deliv date unchanged {err}')
                return deliv_date
