from flask_jsonrpc import JSONRPC
from ..app import app
from config import Config
from ..helpers import OmnisellMessage
from flask import request
from logger import logger

jsonrpc = JSONRPC(app, "/api")


@jsonrpc.method("App.test_point")
def test_point(phone: str, text: str, account: int) -> dict:
    logger.critical(f'Test_poin called with: {phone}, {text}, {account}')
    return {'status': 200,
            'message': 'Test done!'}

@jsonrpc.method("App.send_sms")
def index(phone: str, text: str, account: int) -> dict:
    phone = clear_phone(phone)
    account = check_account(account)
    text = check_text(text)
    conditions = (
        request.headers.get('Authorization', None) != Config.FLASK_CONFIG.SECRET_KEY,
    )
    if all(conditions):
        logger.error('Unauthorized RPC request')
        raise ValueError('Unauthorized')
    if account and text and phone:
        logger.info(f'Successful RPC request: {account}, {phone}, {text} ')
        OmnisellMessage.add_to_db(account, phone, text)
        return {'status': 200,
                'message': 'Ok'}


def clear_phone(phone: str) -> str:
    if len(phone) > 9:
        phone = phone.strip()[-10:]
        if phone.isdigit():
            return '+38'+phone
    logger.error('Invalid phone number')
    raise ValueError('Invalid phone number')


def check_account(account: int) -> int:
    if account:
        if Config.MESSAGE_PARAMS.ACCOUNT_MAX_VALUE > account > 0:
            return account
    logger.error('Invalid account number')
    raise ValueError('Invalid account number')


def check_text(text: str) -> str:
    if text:
        text = text.strip()
        if Config.MESSAGE_PARAMS.MESSAGE_MAX_LENGTH >= len(text) > 0:
            return text
    logger.error('Very long text or no text present')
    raise ValueError('Very long text or no text present')

