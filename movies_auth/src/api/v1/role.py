import json

from flask import Response, request
from http import HTTPStatus

from app.flask_app import urls, db
from models.role import Role, UserRole
from utils.api_utils import create_error_response
from utils.authenticate import authenticate, superuser


@urls.route("/role", methods=["POST"])
@authenticate
@superuser
def role_post():
    """
        Create role
        ---
        tags:
          - Role
        parameters:
        responses:
          200:
            description: Role was created
          409:
            description: Role already exists
    """
    role_instance = Role.fs_get_delete_put_post()
    if isinstance(role_instance, Response):
        return role_instance
    return create_error_response(role_instance)


@urls.route("/role/<role_id>", methods=["PUT"])
@authenticate
@superuser
def role_put(role_id):
    """
        Этот метод обновляет информацию о роли по ее role_id и возвращет обновленную информацию
        ---
        tags:
          - Role
        parameters:
          - in: path
            name: role_id
            type: string
            required: true
        responses:
          200:
            description: A single role item
          404:
            description: Role not found
        """
    role_instance = Role.fs_get_delete_put_post(role_id)
    if isinstance(role_instance, Response):
        return role_instance
    return create_error_response(role_instance)


@urls.route("/user_role_add", methods=["POST"])
@authenticate
@superuser
def user_role_add():
    """
        Set role for user
        ---
        tags:
          - RoleUser
        parameters:
        responses:
          200:
            description: Role was add
          403:
            description: User is not correct
        """
    user_role_instance = UserRole.fs_get_delete_put_post()
    if isinstance(user_role_instance, Response):
        return user_role_instance
    return create_error_response(user_role_instance)


@urls.route("/user_role_revoke", methods=["POST"])
@authenticate
@superuser
def user_role_revoke():
    """
        Delete user role
        ---
        tags:
          - user_role
        parameters:
          - name: body
            in: body
            required: true
            schema:
              id: RoleUser
              properties:
                user_id:
                  type: string
                  required: true
                  description: user_id
                role_id:
                  type: string
                  required: true
                  description: user_id

        responses:
          204:
            description: Delete role
          400:
            description: Error

    """
    user_id = request.json.get("user_id")
    role_id = request.json.get("role_id")
    user_role_instance = UserRole.query.with_entities(UserRole).filter_by(user_id=user_id, role_id=role_id).first()
    db.session.delete(user_role_instance)
    db.session.commit()
    return Response(status=HTTPStatus.NO_CONTENT, headers={"Content-Type": "application/json"})
