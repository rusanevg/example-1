import uuid
from flask_serialize import FlaskSerialize
from sqlalchemy.dialects.postgresql import UUID

from app.flask_app import db

fs_mixin = FlaskSerialize(db)


class User(fs_mixin, db.Model):
    __tablename__ = "user"
    __table_args__ = (
        {
            "schema": "auth",
        },
    )

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(64))
    salt = db.Column(db.String(32))
    is_superuser = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(320), unique=True)

    __fs_create_fields__ = __fs_update_fields__ = ["username", "password", "salt", "email"]

    def __fs_verify__(self, create=False):
        if len(self.username or "") < 1:
            raise Exception("Username is empty")
        if len(self.password or "") < 1:
            raise Exception("Password is empty")
        return True

    def __repr__(self):
        return "<uuid {}>".format(self.uuid)
