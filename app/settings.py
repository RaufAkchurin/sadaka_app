import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    SECRET_KEY: str
    ALGORITHM: str
    MODE: Literal["PROD", "STAGE", "DEV", "TEST"]

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_CALLBACK_URI: str = ""
    GOOGLE_FINAL_REDIRECT_URI: str = ""

    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str
    S3_ENDPOINT_URL: str
    S3_FILE_BASE_URL: str

    POSTGRES_STAGE_USER: str
    POSTGRES_STAGE_PASSWORD: str
    POSTGRES_STAGE_HOST: str
    POSTGRES_STAGE_DB_NAME: str

    POSTGRES_DEV_USER: str
    POSTGRES_DEV_PASSWORD: str
    POSTGRES_DEV_HOST: str
    POSTGRES_DEV_DB_NAME: str

    POSTGRES_TEST_USER: str
    POSTGRES_TEST_PASSWORD: str
    POSTGRES_TEST_HOST: str
    POSTGRES_TEST_DB_NAME: str

    # YOOKASSA PAYMENTS
    YOOKASSA_TEST_SECRET_KEY: str
    YOOKASSA_TEST_SHOP_ID: int

    # T_BANK PAYMENTS V1
    # TBANK_BASE_URL: str = "https://developer.tbank.ru/eacq/api"
    # TBANK_TEST_MERCHANT_ID: str
    # TBANK_TEST_TERMINAL_ID: str
    # TBANK_TEST_SECRET_KEY: str
    # TBNANK_WEBHOOK_SECRET: str = "YOU_WEBHOOK_SECRET"

    T_BANK_API_URL: str = "https://securepay.tinkoff.ru/v2"
    T_BANK_WEBHOOK_URL: str = "https://45a2db004fa3.ngrok-free.app/app/v1/payments/tinkoff/callback"
    T_BANK_TERMINAL_KEY: str = "1752237644677DEMO"
    T_BANK_PASSWORD: str = "bniUwpLIsj1^VkGC"

    SMSC_LOGIN: str
    SMSC_PASSWORD: str

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")

    @property
    def google_redirect_to_service_url(self) -> str:
        return (
            f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={self.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={self.GOOGLE_CALLBACK_URI}&scope=openid%20profile%20email&access_type=offline"
        )

    @property
    def get_base_url(self) -> str | None:
        if self.MODE == "DEV":
            return "http://127.0.0.1:8000/"
        elif self.MODE == "STAGE":
            return "https://sadaka.pro/"
        elif self.MODE == "TEST":
            return "https://test/"
        elif self.MODE == "PROD":
            return "https://YOU_NEED_PRODUCTION_BASE_URL_ON_STTINGS.PY_FILE/"


# Получаем параметры для загрузки переменных среды
settings = Settings()
