from ..app import db
from datetime import datetime


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(150), nullable=False)
    last_modified = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f'Имя: {self.name}'
