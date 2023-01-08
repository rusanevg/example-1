import uuid
from app.flask_app import db
from flask_serialize import FlaskSerialize
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from models.user_agent import UserAgent
from utils.partition_auth_history import create_partition

fs_mixin = FlaskSerialize(db)


class AuthHistory(fs_mixin, db.Model):
    __tablename__ = "auth_history"
    __table_args__ = (
        db.UniqueConstraint("user_agent_id", "auth_date"),
        {
            "postgresql_partition_by": "RANGE (auth_date)",
            "listeners": [("after_create", create_partition)],
            "schema": "auth",
        },
    )

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_agent_id = db.Column(UUID(as_uuid=True), db.ForeignKey(UserAgent.uuid), primary_key=True)
    auth_date = db.Column(db.DateTime(timezone=True), default=func.now())

    __fs_create_fields__ = __fs_update_fields__ = ["user_agent_id", "auth_date"]

    def __init__(self, user_agent_id):
        self.user_agent_id = user_agent_id

    def __repr__(self):
        return "<uuid {}>".format(self.uuid)

    def serialize(self):
        return {
            "uuid": self.uuid,
            "user_agent_id": self.user_agent_id,
            "auth_date": str(self.auth_date)
        }
