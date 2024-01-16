from ..app import db
from datetime import datetime
import enum
# from .collector import MsgCollector


class Channels(enum.Enum):
    SMS = 'SMS'
    OTT = 'OTT'
    OTTSMS = 'OTTSMS'


class MailingListTypes(enum.Enum):
    SINGLE = 'single'
    BULK = 'bulk'
    INDIVIDUAL = 'individual'


class MessageStatuses(enum.Enum):
    ACCEPTED = 'Accepted'
    ENROUTE = 'Enroute'
    DELIVERED = 'Delivered'
    EXPIRED = 'Expired'
    DELETED = 'Deleted'
    UNDELIVERABLE = 'Undeliverable'
    REJECTED = 'Rejected'
    UNKNOWN = 'Unknown'
    INITIAL = 'Initial'


class GroupIdStatuses(enum.Enum):
    INITIAL = 'initial'
    DONE = 'done'
    CANCELED = 'canceled'


class OmnicellTasks(db.Model):
    __tablename__ = "omnicell"
    id = db.Column(db.Integer, primary_key=True)

    message_id = db.Column(db.Integer, db.ForeignKey('msgcollector.id'))
    message = db.relationship('MsgCollector', backref='tasks')

    status = db.Column(db.Enum(MessageStatuses), nullable=False, default=MessageStatuses.INITIAL.value,
                       server_default=MessageStatuses.INITIAL.value)
    remote_message_id = db.Column(db.String(20), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group_ids.group_id'))
    groups = db.relationship('GroupIds', backref='groups', lazy='select')
    channel = db.Column(db.Enum(Channels), nullable=False, default=Channels.SMS.value,
                        server_default=Channels.SMS.value)
    mailing_list_type = db.Column(db.Enum(MailingListTypes), nullable=False, default=MailingListTypes.INDIVIDUAL.value,
                                  server_default=MailingListTypes.INDIVIDUAL.value)
    last_modified = db.Column(db.DateTime, nullable=False, default=datetime.now)
    delivery_date = db.Column(db.DateTime, nullable=True)


class GroupIds(db.Model):
    __tablename__ = "group_ids"
    group_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum(GroupIdStatuses), nullable=False, default=GroupIdStatuses.INITIAL.value,
                       server_default=GroupIdStatuses.INITIAL.value)

    def __repr__(self):
        return f'Группа: {self.group_id}\nСтатус: {self.status.value}'


class MyEnums:
    statuses = MessageStatuses
    mailing_list_types = MailingListTypes
    channels = Channels
    # message_extended_statuses = MessageExtendedStatuses
    group_id_statuses = GroupIdStatuses


class OmnicellModel:
    omnicell_tasks = OmnicellTasks
    enums = MyEnums
    group_ids = GroupIds
