from typing import Dict, Union, Any
from os import getenv, getcwd, pardir, sep, mkdir
from os.path import abspath, join, exists
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class Service:
    @staticmethod
    def props_to_dict(obj: Any) -> Dict[str, Union[str, int, bool]]:
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_') and k.isupper()}


class DbConfig:
    DB_USER = getenv('DB_USER')
    DB_PWD = getenv('DB_PWD')
    DB_HOST = getenv('DB_HOST')
    DB_PORT = getenv('DB_PORT')
    DB_NAME = getenv('DB_NAME')
    DB_URL = f'mysql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}'
    SQLALCHEMY_DATABASE_URI = f'mysql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class FlaskConfig:
    HOST = getenv('HOST')
    PORT = getenv('PORT')
    template_folder = '/templates'
    TESTING = getenv('TESTING') == 'True'
    DEBUG = getenv('DEBUG') == 'True'
    SECRET_KEY = getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = DbConfig.SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def config() -> dict:
        return Service.props_to_dict(FlaskConfig)


class Credentials:
    OMNISELL_USER = getenv('OMNISELL_USER')
    OMNISELL_PWD = getenv('OMNISELL_PWD')


class OmnicellUrls:
    SEND_SMS = getenv('SEND_SMS')
    SMS_STATUS = getenv('SMS_STATUS')


class Urls:
    OMNICELL = OmnicellUrls


class ShedulerParams:
    START_WORK = datetime.strptime(getenv('START_WORK'), '%H:%M').time()
    FINISH_WORK = datetime.strptime(getenv('FINISH_WORK'), '%H:%M').time()
    EMAIL_REPORT_TIME = getenv('EMAIL_REPORT_TIME')
    SMS_SENDING_TIME = getenv('SMS_SENDING_TIME')
    SMS_GET_STATUS_TIME = getenv('SMS_GET_STATUS_TIME')
    FREQUENCY = int(getenv('FREQUENCY'))


class EmailParams:
    SMTP_SERVER = getenv('SMTP_SERVER')
    SMTP_PORT = getenv('SMTP_PORT')
    SENDER_EMAIL = getenv('SENDER_EMAIL')
    RECEIVER_EMAIL = getenv('RECEIVER_EMAIL')
    MESSAGE_SUBJECT = getenv('MESSAGE_SUBJECT')
    RECEIVERS_EMAIL = ",".join(RECEIVER_EMAIL.split(';'))


class MessageParams:
    _MESSAGE_MAX_LENGTH = getenv('MESSAGE_MAX_LENGTH')
    MESSAGE_MAX_LENGTH = int(_MESSAGE_MAX_LENGTH) if _MESSAGE_MAX_LENGTH.isdigit() else 210
    _ACCOUNT_MAX_VALUE = getenv('ACCOUNT_MAX_VALUE')
    ACCOUNT_MAX_VALUE = int(_ACCOUNT_MAX_VALUE) if _ACCOUNT_MAX_VALUE.isdigit() else 99999999


class Config:
    FLASK_CONFIG = FlaskConfig
    URLS = Urls
    CREDS = Credentials
    ALPHANAME = getenv('ALPHANAME')
    DATABASE = DbConfig
    SHEDULER_PARAMS = ShedulerParams
    EMAIL_PARAMS = EmailParams
    CHANNEL = getenv('CHANNEL')
    TTL = int(getenv('TTL'))
    MESSAGE_PARAMS = MessageParams
    BASE_DIR = abspath(getcwd())
    TEMPLATES_DIR = abspath(join(BASE_DIR, f'server{sep}templates'))
    STATIC_DIR = abspath(join(BASE_DIR, f'server{sep}static'))
    PATH_SEP = sep
    LOG_FILE = abspath(join(BASE_DIR, f'logs{sep}app.log'))
    LOG_PATH = abspath(join(BASE_DIR, 'logs'))
    @classmethod
    def logpath(cls):
        if not exists(cls.LOG_PATH):
            mkdir(cls.LOG_PATH)
        return cls.LOG_FILE