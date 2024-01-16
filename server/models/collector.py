from ..app import db
from datetime import datetime
import enum


class MessageStatuses(enum.Enum):
    INITIAL = 'initial'
    PROCESSED = 'processed'


class MsgCollector(db.Model):
    __tablename__ = "msgcollector"
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(13), nullable=False)
    text = db.Column(db.String(1024), nullable=False)
    status = db.Column(db.Enum(MessageStatuses), nullable=False, default=MessageStatuses.INITIAL.value,
                       server_default=MessageStatuses.INITIAL.value)
    last_modified = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f'Телефон: {self.phone}\nТекст: {self.text}'

    @property
    def for_omnicell(self) -> dict:
        return {
            "msisdn": self.phone,
            "body": {
                "value": self.text
            }
        }


class CollectorModels:
    statuses = MessageStatuses
    collector = MsgCollector
