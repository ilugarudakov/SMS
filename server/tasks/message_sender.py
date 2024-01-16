from config import Config
from schedule import run_pending, every, repeat
from time import sleep
from threading import Thread
from datetime import datetime
from .email_report import EmailReport
from ..controllers import MailingMaker
from logger import logger
from ..helpers import OmnisellTask


class Scheduler:
    @staticmethod
    def is_worktime() -> bool:
        logger.info('Worker active time started')
        now = datetime.now().time()
        return Config.SHEDULER_PARAMS.START_WORK <= now <= Config.SHEDULER_PARAMS.FINISH_WORK

    @staticmethod
    # @repeat(every(Config.SHEDULER_PARAMS.FREQUENCY).seconds)
    @repeat(every().day.at(Config.SHEDULER_PARAMS.SMS_SENDING_TIME))
    def _do_send_sms():
        if Scheduler.is_worktime:
            logger.info('Create mailing started')
            MailingMaker.create_mailing()

    @staticmethod
    @repeat(every(Config.SHEDULER_PARAMS.FREQUENCY).seconds)
    # @repeat(every().day.at(Config.SHEDULER_PARAMS.SMS_GET_STATUS_TIME))
    def _do_update_sms_statuses():
        logger.info('Updating message statuses')
        try:
            OmnisellTask().update_individual_accepted_tasks()  # уточняем статусы принятых к отправке груп сообщений
        except Exception as ex:
            logger.warning(f'Cant update individual accepted task statuses. Reason: {ex}')
        try:
            OmnisellTask().update_single_accepted_tasks()  # уточняем статусы принятых к отправке единичных сообщений
        except Exception as ex:
            logger.warning(f'Cant update single accepted task statuses. Reason: {ex}')


    @staticmethod
    @repeat(every().day.at(Config.SHEDULER_PARAMS.EMAIL_REPORT_TIME))
    def _do_send_email():
        logger.info('Making email report')
        er = EmailReport()
        task = Thread(target=er.send_email, args=(Config.EMAIL_PARAMS.RECEIVERS_EMAIL,))
        task.run()

    @staticmethod
    def run_all() -> None:
        while True:
            sleep(1)
            run_pending()

    @classmethod
    def start(cls):
        cls.run_all()
