from requests import Response, post
from requests.auth import HTTPBasicAuth
from random import randint
from config import Config
from typing import List, Union
from ..models import OmnicellModel
from logger import logger


class OmnisellRequest:
    def __init__(self):
        self.data = None
        self.url = None
        self.headers = {'Host': 'api.omnicell.com.ua',
                        'Content-type': 'application/json;charset=UTF-8',
                        'Accept': 'application/json',
                        'user-agent': 'SMS server'
                        }
        self.auth = HTTPBasicAuth(Config.CREDS.OMNISELL_USER, Config.CREDS.OMNISELL_PWD)

    def send_single(self, text, phone) -> Union[Response, bool]:
        if text and phone:
            self.url = Config.URLS.OMNICELL.SEND_SMS
            self.data = {
                "id": 'single',
                "validity": "+30 min",
                "source": Config.ALPHANAME,
                "desc": 'Webform message',
                "type": OmnicellModel.enums.channels.SMS.value,  # SMS
                "to": [
                        {"msisdn": phone}
                ],
                "body": {"value": text}
                }
            return self.make_query()
        return False

    def send(self, tasks: List[OmnicellModel.omnicell_tasks]) -> Union[Response, bool]:
        if tasks:
            self.url = Config.URLS.OMNICELL.SEND_SMS
            self.data = {
                "uniq_key": randint(10000000, 99999999),
                "id": OmnicellModel.enums.mailing_list_types.INDIVIDUAL.value,  # INDIVIDUAL
                "source": Config.ALPHANAME,
                "desc": 'Payment remind',
                "type": OmnicellModel.enums.channels.SMS.value,  # SMS
                "to": [elem.message.for_omnicell for elem in tasks]
            }
            return self.make_query()
        return False

    def get_accepted_statuses(self, groupid: int) -> Union[Response, bool]:
        self.url = Config.URLS.OMNICELL.SMS_STATUS
        self.data = {
            "extended": True,
            "groupid": groupid,
            "value": "details"
        }
        return self.make_query()

    def get_single_accepted_statuses(self, id: int) -> Union[Response, bool]:
        self.url = Config.URLS.OMNICELL.SMS_STATUS
        self.data = {
            "extended": True,
            "id": id,
            "value": "state"
        }
        return self.make_query()

    def make_query(self) -> Union[Response, bool]:
        try:
            response = post(url=self.url, auth=self.auth, headers=self.headers, json=self.data)

            logger.info(f' post data: url={self.url}, auth={self.auth}, headers={self.headers}, json={self.data}')
            logger.info(f' response={response.text}')

            return response
        except Exception as e:
            logger.error(f'Remote server: {self.url} not response', e)
            return False
