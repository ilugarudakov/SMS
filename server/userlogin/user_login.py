from flask_login import UserMixin
from ..models import Users


class UserLogin(UserMixin):
    def fromDB(self, user_id):
        user = Users()
        self.__user = user.query.filter_by(id=user_id).first()
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user.id)

    def getName(self):
        return str(self.__user.name) if self.__user else "Без имени"
