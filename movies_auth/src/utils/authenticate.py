from datetime import datetime
from flask import Response, request, session

from app.flask_app import cache
from core.config import app_config
from http import HTTPStatus

from models.user import User
from utils.api_utils import decode_access_token


def authenticate(func):
    def inner(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if auth_header:
            access_token = auth_header.split(" ")[-1]
            invalid_jwt = cache.get(f"{app_config.INVALID_JWT_PREFIX}{access_token}")
            # проверяем, занесён ли токен в список невалидных
            if invalid_jwt is None:
                payload = decode_access_token(access_token)
                expire = int(payload["exp"] - (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())
                # проверяем, не истёк ли срок действия токена
                if expire > 0:
                    user_id = payload["user_id"]
                    invalidate_for_user = cache.get(f"{app_config.INVALIDATE_JWT_FOR_USER}{user_id}")
                    # проверяем, есть ли требование обновить токен для пользователя
                    if invalidate_for_user is None:
                        return func(*args, **kwargs)
                    else:
                        cache.delete(f"{app_config.INVALIDATE_JWT_FOR_USER}{user_id}")
                        cache.set(f"{app_config.INVALID_JWT_PREFIX}{access_token}", "", ex=expire)
        return Response("Access token invalid", status=HTTPStatus.UNAUTHORIZED)
    inner.__name__ = func.__name__
    return inner


def superuser(func):
    def inner(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id:
            user = User.query.with_entities(User).filter_by(uuid=user_id).first()
            if user and user.is_superuser:
                return func(*args, **kwargs)
        return Response("User is not superuser", status=HTTPStatus.UNAUTHORIZED)
    inner.__name__ = func.__name__
    return inner
