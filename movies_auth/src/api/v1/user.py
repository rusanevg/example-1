from flask import Response, request, session

from app.flask_app import urls
from models.user import User
from utils.api_utils import generate_password_hash, create_error_response
from utils.authenticate import authenticate
from utils.rate_limit import rate_limit


@urls.route("/user", methods=["POST"])
def user_post():
    """
    Post method for users
        ---
        tags:
          - user
        parameters:
          - in: body
            name: body
            schema:
              id: UserLogin
              properties:
                username:
                  type: string
                  description: The user's username.
                  required: true
                password:
                  type: string
                  description: The user's password.
                  required: true
                email:
                  type: string
                  description: The user's email.
        responses:
          200:
            description: User create
          400:
            description: User already exists
    """
    if request.json.get("password"):
        pwd_hash, salt = generate_password_hash(request.json["password"])
        request.json["password"] = pwd_hash
        request.json["salt"] = salt
    user_instance = User.fs_get_delete_put_post()
    if isinstance(user_instance, Response):
        return user_instance
    return create_error_response(user_instance)


@urls.route("/user", methods=["PUT"])
@authenticate
def user_put():
    """
        Update user data
        ---
        tags:
          - user
        parameters:
          - name: body
            in: body
            schema:
              id: User
              properties:
                username:
                  type: string
                  description: The user's username.
                password:
                  type: string
                  description: The user's password.
                email:
                  type: string
                  description: The user's email.
        responses:
          200:
            description: User data updated
          400:
            description: User data incorrect
    """
    if request.json.get("password"):
        pwd_hash, salt = generate_password_hash(request.json["password"])
        request.json["password"] = pwd_hash
        request.json["salt"] = salt
    user_instance = User.fs_get_delete_put_post(session.get("user_id"))
    if isinstance(user_instance, Response):
        return user_instance
    return create_error_response(user_instance)
