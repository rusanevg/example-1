import ast
import binascii
import json
import jwt
import random
import re
import string
import time
from backports.pbkdf2 import pbkdf2_hmac
from flask import Response
from http import HTTPStatus
import requests
from core.config import app_config


def generate_random_string(length: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=length))


def generate_password_hash(password: str, salt: str = None) -> tuple():
    """
    :param salt: соль
    :param password: пароль
    :return: захешированный пароль и соль
    """
    if not salt:
        salt = "".join(generate_random_string(32))
    key_unhex = pbkdf2_hmac("sha256", password.encode("utf8"), salt.encode("utf8"), 100000, 32)
    return binascii.hexlify(key_unhex).decode("utf8"), salt


def encode_access_token(user_id, user_agent_id) -> str:
    """
    :return: JWT токен
    """
    user_subscriptions = get_subscriptions_by_user_id(user_id=user_id)
    payload = {
        "exp": time.time() + app_config.ACCESS_TOKEN_LIVING_TIME_SEC,
        "iat": time.time(),
        "user_id": str(user_id),
        "user_agent_id": str(user_agent_id),
        "subscriptions": user_subscriptions,
    }
    return jwt.encode(payload, app_config.SECRET_KEY, algorithm="HS256")


def get_subscriptions_by_user_id(user_id):
    payload = {
        "exp": time.time() + 60,
        "iat": time.time() - 1,
        "user_id": "00000000-0000-0000-0000-000000000000",
        "user_agent_id": "00000000-0000-0000-0000-000000000000"
    }
    token = jwt.encode(payload, app_config.SECRET_KEY, algorithm="HS256")
    resp = requests.get(f"{app_config.SUBSCRIPTION_ENDPOINT}{user_id}", headers={"Authorization": token})
    if resp.status_code == HTTPStatus.OK:
        return ast.literal_eval(resp.content.decode("utf-8"))
    else:
        return []


def decode_access_token(access_token):
    """
    :return: данные из JWT токена
    """
    return jwt.decode(access_token, app_config.SECRET_KEY, algorithms="HS256")


def create_error_response(items):
    detail = re.search(r'DETAIL:  (.+)', items[0])
    if detail:
        body = {
            "error": detail.group(1)
        }
    else:
        body = {
            "error": items[0]
        }
    return Response(json.dumps(body), status=items[1], headers={"Content-Type": "application/json"})
