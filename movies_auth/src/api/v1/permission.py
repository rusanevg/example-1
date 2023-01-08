import json

from flask import Response, request
from http import HTTPStatus

from app.flask_app import urls, db
from models.permission import Permission, RolePermission
from models.role import UserRole
from utils.api_utils import create_error_response
from utils.authenticate import authenticate, superuser


@urls.route("/permission", methods=["POST"])
@authenticate
@superuser
def permission_post():
    """
        Create permission
        ---
        tags:
          -permission
        parameters:
        responses:
          200:
            description: Success permission post
    """
    permission_instance = Permission.fs_get_delete_put_post()
    if isinstance(permission_instance, Response):
        return permission_instance
    return create_error_response(permission_instance)


@urls.route("/permission/<permission_id>", methods=["PUT"])
@authenticate
@superuser
def permission_put(permission_id):
    """
        Update permission data
        ---
        tags:
          - permission
        parameters:
          - in: path
            name: permission_id
            type: string
            required: true
        responses:
          200:
            description: Permission update
          404:
            description: permission not found
    """
    permission_instance = Permission.fs_get_delete_put_post(permission_id)
    if isinstance(permission_instance, Response):
        return permission_instance
    return create_error_response(permission_instance)


@urls.route("/role_permission_add", methods=["POST"])
@authenticate
@superuser
def role_permission_add():
    """
        Add role permission
        ---
        tags:
          - permission
        parameters:
          - name: body
            in: body
            required: true
            schema:
              id: UserPermission
              properties:
                user_id:
                  type: string
                  required: true
                  description: user_id
                permission_id:
                  type: string
                  required: true
                  description: permission_id

        responses:
          200:
            description: Permission add
          400
            description: Error

    """
    role_permission_instance = RolePermission.fs_get_delete_put_post()
    if isinstance(role_permission_instance, Response):
        return role_permission_instance
    return create_error_response(role_permission_instance)


@urls.route("/role_permission_revoke", methods=["POST"])
@authenticate
@superuser
def role_permission_revoke():
    """
        Revoke role permission
        ---
        tags:
          - permission
        parameters:
          - name: body
            in: body
            required: true
            schema:
              id: UserPermission
              properties:
                user_id:
                  type: string
                  required: true
                  description: user_id
                permission_id:
                  type: string
                  required: true
                  description: permission_id

        responses:
          204:
            description: Permission was delete
          400:
            description: Error

    """
    role_id = request.json.get("role_id")
    permission_id = request.json.get("permission_id")
    role_permission_instance = RolePermission.query.with_entities(RolePermission).\
        filter_by(role_id=role_id, permission_id=permission_id).first()
    db.session.delete(role_permission_instance)
    db.session.commit()
    return Response(status=HTTPStatus.NO_CONTENT, headers={"Content-Type": "application/json"})


@urls.route("/check_permission", methods=["POST"])
@authenticate
def check_permission():
    """
        Check permission
        ---
        tags:
          - permission
        parameters:
          - name: body
            in: body
            required: true
            schema:
              id: UserPermission
              properties:
                user_id:
                  type: string
                  required: true
                  description: user_id
                permission_name:
                  type: string
                  required: true
                  description: permission_name

        responses:
          200:
            description: Result of check
          400:
            description: Error

    """
    user_id = request.json.get("user_id")
    permission_name = request.json.get("permission_name")
    permission = Permission.query.with_entities(Permission).filter_by(name=permission_name).first()
    if permission:
        user_roles_ids = UserRole.query.with_entities(UserRole.role_id).filter_by(user_id=user_id)
        role_permission_instance = RolePermission.query.with_entities(RolePermission).\
            filter_by(permission_id=permission.uuid).\
            filter(RolePermission.role_id.in_(user_roles_ids)).first()
        if role_permission_instance:
            return Response(json.dumps({"result": True}), status=HTTPStatus.OK, headers={"Content-Type": "application/json"})
    return Response(json.dumps({"result": False}), status=HTTPStatus.OK, headers={"Content-Type": "application/json"})
