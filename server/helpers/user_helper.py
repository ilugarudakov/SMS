from ..models import Users
from logger import logger


class UserHelper:
    @staticmethod
    def get_user_by_name(username: str):
        try:
            user = Users()
            res = user.query.filter_by(name=username).first()
            if not res:
                logger.warning('User not found')
            return res
        except Exception as e:
            logger.error('Error connecting to db' + str(e))
        return False
