import os
from functools import lru_cache
from logging import config as logging_config
from pydantic import BaseSettings, Field

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    # Корень проекта
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Секретный ключ
    SECRET_KEY: str = Field("random_key")

    # Настройки Redis
    REDIS_HOST: str = Field("REDIS_HOST")
    REDIS_PORT: int = Field(6379)

    # Настройки SQLAlchemy
    DB_AUTH_HOST: str = Field("DB_AUTH_HOST")
    DB_USER: str = Field("DB_USER")
    DB_PASSWORD: str = Field("DB_PASSWORD")
    DB_AUTH_NAME: str = Field("DB_AUTH_NAME")
    DB_AUTH_PORT: int = Field("DB_AUTH_PORT")

    # Настройки для токенов
    ACCESS_TOKEN_LIVING_TIME_SEC: int = Field(3600)
    REFRESH_TOKEN_LIVING_TIME_SEC: int = Field(3600 * 24 * 10)
    INVALID_JWT_PREFIX: str = Field("invalid_jwt_")
    INVALIDATE_JWT_FOR_USER: str = Field("invalidate_jwt_for_user_")
    REFRESH_TOKEN_PREFIX: str = Field("refresh_token_")

    GOOGLE_CLIENT_ID: str = Field("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL: str = Field("https://accounts.google.com/.well-known/openid-configuration")
    GOOGLE_SOCIAL_NAME: str = Field("google")

    # Настройки Yandex
    YANDEX_SOCIAL_NAME: str = Field("yandex")
    YANDEX_CLIENT_ID: str = Field("YANDEX_CLIENT_ID")
    YANDEX_CLIENT_SECRET: str = Field("YANDEX_CLIENT_SECRET")
    YANDEX_AUTHORIZATION_ENDPOINT: str = Field("YANDEX_AUTHORIZATION_ENDPOINT")
    YANDEX_USERINFO_ENDPOINT: str = Field("YANDEX_USERINFO_ENDPOINT")
    YANDEX_TOKEN_ENDPOINT: str = Field("YANDEX_TOKEN_ENDPOINT")

    ENABLE_TRACER: bool = Field(True)

    SUBSCRIPTION_ENDPOINT: str = Field("http://subscription-api:8005/api/v1/subscriptions/")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


app_config = get_settings()
