import json
from flask import Response, request, session
from http import HTTPStatus

from app.flask_app import cache, urls
from core.config import app_config
from utils.api_utils import generate_random_string, encode_access_token, create_error_response
from utils.authenticate import authenticate


@urls.route("/refresh_token", methods=["POST"])
@authenticate
def refresh_token():
    """
        Update token
        ---
        tags:
          - user
        parameters:
          - name: Authorization
            in: header
            schema:
              properties:
                refresh_token:
                  type: string
                  required: true
                  description: Refresh token.
        responses:
          200:
            description: Tokens updated
          401:
            description: Invalid refresh token
    """
    token = request.json.get("refresh_token")
    cached_token = cache.get(f"{app_config.REFRESH_TOKEN_PREFIX}{session.get('user_agent_id')}")
    if token == cached_token:
        # создаём новый refresh_token для user_agent и сохраняем его в кеше
        new_token = generate_random_string(32)
        cache.set(f"{app_config.REFRESH_TOKEN_PREFIX}{session.get('user_agent_id')}", new_token,
                  ex=app_config.REFRESH_TOKEN_LIVING_TIME_SEC)
        # создаём access_token и отправляем его и refresh_token в ответе
        access_token = encode_access_token(session.get("user_id"), session.get("user_agent_id"))
        payload = {
            "access_token": access_token,
            "refresh_token": new_token
        }
        return Response(json.dumps(payload), status=HTTPStatus.OK, headers={"Content-Type": "application/json"})
    # если полученный и сохранённый токены не совпадают, возвращаем 401
    return create_error_response(("Invalid refresh token", HTTPStatus.UNAUTHORIZED))
