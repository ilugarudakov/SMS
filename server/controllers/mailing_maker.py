from config import Config
from .omnicell import Omnicell
from logger import logger


class MailingMaker:
    @staticmethod
    def create_mailing():
        if Config.CHANNEL == 'omnicell':
            Omnicell().create_mailing()
        else:
            logger.error(f'Unknown channel: {Config.CHANNEL}')
            raise EnvironmentError(f'Unknown channel: {Config.CHANNEL}')
