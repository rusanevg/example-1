import os
from functools import lru_cache
from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    # Корень проекта
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Секретный ключ
    SECRET_KEY: str = Field("SECRET_KEY")

    # Настройки Redis
    REDIS_HOST: str = Field("test-redis")
    REDIS_PORT: int = Field(6379)

    # Настройки SQLAlchemy
    DB_HOST: str = Field("test-postgres")
    DB_NAME: str = Field("auth_database")
    DB_USER: str = Field("test_user")
    DB_PASSWORD: str = Field("test_password")

    # Настройки для токенов
    ACCESS_TOKEN_LIVING_TIME_SEC: int = Field(3600)
    REFRESH_TOKEN_LIVING_TIME_SEC: int = Field(3600 * 24 * 10)
    INVALID_JWT_PREFIX: str = Field("invalid_jwt_")
    REFRESH_TOKEN_PREFIX: str = Field("refresh_token_")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> TestSettings:
    return TestSettings()


test_settings = get_settings()
