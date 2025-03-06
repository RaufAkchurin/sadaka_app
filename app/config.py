import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    SECRET_KEY: str
    ALGORITHM: str
    TESTING: int
    ENVIRONMENT: str

    TEST_POSTGRES_PASSWORD: str
    TEST_POSTGRES_USER: str
    TEST_POSTGRES_DB: str
    TEST_POSTGRES_HOST: str
    TEST_POSTGRES_PORT: int

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")

# Получаем параметры для загрузки переменных среды
settings = Settings()

if settings.TESTING == 1:
    database_url = (
        f"postgresql+asyncpg://{settings.TEST_POSTGRES_USER}:{settings.TEST_POSTGRES_PASSWORD}@{settings.TEST_POSTGRES_HOST}:{settings.TEST_POSTGRES_PORT}/{settings.TEST_POSTGRES_DB}"
    )
else:
    database_url = f"sqlite+aiosqlite:///{settings.BASE_DIR}/data/db.sqlite3"





