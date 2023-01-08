import uuid
from app.flask_app import db
from flask_serialize import FlaskSerialize
from sqlalchemy.dialects.postgresql import UUID

from models.user import User

fs_mixin = FlaskSerialize(db)


class UserAgent(fs_mixin, db.Model):
    __tablename__ = "user_agent"
    __table_args__ = (
        db.UniqueConstraint("user_id", "name"),
        {
            "schema": "auth",
        },
    )

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(User.uuid), primary_key=True)
    name = db.Column(db.String(255))

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

    __fs_create_fields__ = __fs_update_fields__ = ["user_id", "name"]

    def __repr__(self):
        return "<uuid {}>".format(self.uuid)
