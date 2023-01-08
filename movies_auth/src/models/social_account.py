import uuid
from flask_serialize import FlaskSerialize
from sqlalchemy.dialects.postgresql import UUID

from app.flask_app import db
from models.user import User

fs_mixin = FlaskSerialize(db)


class SocialAccount(fs_mixin, db.Model):
    __tablename__ = "social_account"
    __table_args__ = (
        db.UniqueConstraint("social_id", "social_name"),
        {
            "schema": "auth",
        },
    )

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(User.uuid), primary_key=True)
    social_id = db.Column(db.String(64))
    social_name = db.Column(db.String(32))

    __fs_create_fields__ = __fs_update_fields__ = ["user_id", "social_id", "social_name"]

    def __repr__(self):
        return "<uuid {}>".format(self.uuid)
