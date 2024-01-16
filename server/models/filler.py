from .collector import CollectorModels
from .users import Users
from ..app import db
from werkzeug.security import generate_password_hash, check_password_hash

#
# class StartData:
#     @staticmethod
#     def fill() -> None:
#         res = CollectorModels.collector.query.first()
#         if not res:
#             user = Users()
#             user.name = 'admin'
#             user.password = generate_password_hash('211')
#
#             db.session.add(user)
#             db.session.commit()