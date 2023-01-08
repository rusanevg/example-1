import uuid
from app.flask_app import db
from flask_serialize import FlaskSerialize
from sqlalchemy.dialects.postgresql import UUID

from models.role import Role

fs_mixin = FlaskSerialize(db)


class Permission(fs_mixin, db.Model):
    __tablename__ = "permission"
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


class RolePermission(fs_mixin, db.Model):
    __tablename__ = "role_permission"
    __table_args__ = (
        db.UniqueConstraint("role_id", "permission_id"),
        {
            "schema": "auth",
        },
    )

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey(Role.uuid), primary_key=True)
    permission_id = db.Column(UUID(as_uuid=True), db.ForeignKey(Permission.uuid), primary_key=True)

    __fs_create_fields__ = __fs_update_fields__ = ["role_id", "permission_id"]

    def __repr__(self):
        return "<uuid {}>".format(self.uuid)
