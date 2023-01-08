import json
import jwt
from datetime import datetime
from flask import Response, request, session
from http import HTTPStatus

from app.flask_app import urls, db, cache
from core.config import app_config
from models.auth_history import AuthHistory
from models.user import User
from models.user_agent import UserAgent
from utils.api_utils import generate_random_string, generate_password_hash, encode_access_token, decode_access_token, \
    create_error_response
from utils.authenticate import authenticate


@urls.route("/login", methods=["POST"])
def login():
    """
        Login method for users
        ---
        tags:
          - auth
        parameters:
          - in: body
            name: body
            schema:
              id: UserLogin
              required:
                - username
                - password
              properties:
                username:
                  type: string
                  description: The user's username.
                  default: "JohnDoe"
                password:
                  type: string
                  description: The user's password.
                  default: "Qwerty123"
        responses:
          200:
            description: Success user's login
            schema:
              properties:
                success:
                  type: boolean
                  description: Response status
                  default: True
                data:
                  type: array
                  description: Response data
                  items:
                    type: object
                    properties:
                      access_token:
                        type: string
                      refresh_token:
                        type: string
                message:
                  type: string
                  description: Response message
          401:
            description: Invalid credentials
            schema:
              properties:
                success:
                  type: boolean
                  description: Response status
                  default: False
                data:
                  type: array
                  description: Response data
                  items:
                    type: object
                    default: ...
                  default: []
                message:
                  type: string
                  description: Response message
        """
    username = request.json.get("username")
    user = User.query.with_entities(User).filter_by(username=username).first()
    if user:
        pwd_hash, _ = generate_password_hash(request.json.get("password"), user.salt)
        # проверяем соответствие хешей полученного и сохраненного паролей
        if pwd_hash == user.password:
            return success_login_callback(user.uuid)
    # если пользователь не найден или хеши паролей не совпадают, возвращаем 401
    return create_error_response(("Invalid credentials", HTTPStatus.UNAUTHORIZED))


# !!! ВАЖНО указывать @authenticate декоратор после @urls.route !!!
@urls.route("/logout", methods=["GET"])
@authenticate
def logout():
    """
        User logout
        ---
        tags:
          - auth
        parameters:
          - name: body
            in: header
            schema:
              properties:
                access_token:
                  type: string
                  required: true
                  description: Access token

        responses:
          204:
            description: Succesfully logged out
          401:
            description: Token problem
    """
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header:
            access_token = auth_header.split(" ")[-1]
            payload = decode_access_token(access_token)
            cache.delete(f"{app_config.REFRESH_TOKEN_PREFIX}{payload['user_agent_id']}")
            expire = int(payload["exp"] - (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())
            cache.set(f"{app_config.INVALID_JWT_PREFIX}{access_token}", "", ex=expire)
            return Response(status=HTTPStatus.NO_CONTENT, headers={"Content-Type": "application/json"})
    except jwt.ExpiredSignatureError:
        return create_error_response(("Expired token", HTTPStatus.UNAUTHORIZED))
    except jwt.InvalidTokenError:
        return create_error_response(("Invalid token", HTTPStatus.UNAUTHORIZED))


@urls.route("/check_token", methods=["GET"])
@authenticate
def check_token():
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header:
            access_token = auth_header.split(" ")[-1]
            payload = decode_access_token(access_token)
            return Response(json.dumps(payload), status=HTTPStatus.OK, headers={"Content-Type": "application/json"})
    except jwt.ExpiredSignatureError:
        return create_error_response(("Expired token", HTTPStatus.UNAUTHORIZED))
    except jwt.InvalidTokenError:
        return create_error_response(("Invalid token", HTTPStatus.UNAUTHORIZED))


@urls.route("/invalidate_access_token", methods=["POST"])
def invalidate_access_token():
    user_id = request.json.get("user_id")
    if user_id:
        cache.set(f"{app_config.INVALIDATE_JWT_FOR_USER}{user_id}", "", ex=app_config.ACCESS_TOKEN_LIVING_TIME_SEC)
        return Response(status=204, headers={"Content-Type": "application/json"})
    else:
        return Response(status=400, headers={"Content-Type": "application/json"})


def success_login_callback(user_id: str) -> Response:
    user_agent_header = request.headers["User-Agent"][:255]
    user_agent = UserAgent.query.with_entities(UserAgent) \
        .filter_by(user_id=user_id, name=user_agent_header).first()
    # если user_agent не существует, создаём нового
    if not user_agent:
        user_agent = UserAgent(user_id=user_id, name=user_agent_header)
        db.session.add(user_agent)
        db.session.commit()
    # сохраняем данные в сессии
    session["user_id"] = user_id
    session["user_agent_id"] = user_agent.uuid
    # создаём запись об успешной аутентификации
    db.session.add(AuthHistory(user_agent_id=user_agent.uuid))
    db.session.commit()
    # создаём новый refresh_token для user_agent и сохраняем в кеше
    refresh_token = generate_random_string(32)
    cache.set(f"{app_config.REFRESH_TOKEN_PREFIX}{user_agent.uuid}", refresh_token,
              ex=app_config.REFRESH_TOKEN_LIVING_TIME_SEC)
    # создаём access_token и отправляем его и refresh_token в ответе
    access_token = encode_access_token(user_id, str(user_agent.uuid))
    payload = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    return Response(json.dumps(payload), status=HTTPStatus.OK, headers={"Content-Type": "application/json"})
