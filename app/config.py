import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    SECRET_KEY: str
    ALGORITHM: str
    MODE: Literal["PROD", "DEV", "TEST"]

    TEST_POSTGRES_PASSWORD: str
    TEST_POSTGRES_USER: str
    TEST_POSTGRES_DB: str
    TEST_POSTGRES_HOST: str
    TEST_POSTGRES_PORT: int

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")

# Получаем параметры для загрузки переменных среды
settings = Settings()







