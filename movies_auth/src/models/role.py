import uuid
from app.flask_app import db
from flask_serialize import FlaskSerialize
from sqlalchemy.dialects.postgresql import UUID

from models.user import User

fs_mixin = FlaskSerialize(db)


class Role(fs_mixin, db.Model):
    __tablename__ = "role"
    __table_args__ = (
        {
            "schema": "auth",
        },
    )

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), unique=True)

    __fs_create_fields__ = __fs_update_fields__ = ["name"]

    def __repr__(self):
        return "<uuid {}>".format(self.uuid)


class UserRole(fs_mixin, db.Model):
    __tablename__ = "user_role"
    __table_args__ = (
        db.UniqueConstraint("user_id", "role_id"),
        {
            "schema": "auth",
        },
    )

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(User.uuid), primary_key=True)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey(Role.uuid), primary_key=True)

    __fs_create_fields__ = __fs_update_fields__ = ["user_id", "role_id"]

    def __repr__(self):
        return "<uuid {}>".format(self.uuid)
