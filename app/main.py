import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from yookassa import Configuration as YookassaConfiguration

from app.admin.register import create_admin_panel
from app.profiler import TimingMiddleware, setup_pool_logging, setup_sql_logging
from app.settings import settings
from app.v1.auth.router import v1_auth_router, v2_auth_router
from app.v1.auth_google.router import v1_google_router
from app.v1.auth_sms.router import v1_auth_sms_router
from app.v1.city.router import v1_cities_router
from app.v1.comment.router import v1_comment_router
from app.v1.dao.database import engine
from app.v1.fund.router import v1_funds_router
from app.v1.payment_core.router import v1_payments_core_router
from app.v1.payment_t_bank2.router import v1_t_bank_router_2
from app.v1.payment_yookassa.router import v1_yookassa_router
from app.v1.project.router import v1_projects_router
from app.v1.rating.router import v1_rating_router
from app.v1.referrals.router import v1_referral_router
from app.v1.s3_storage.router import v1_s3_router
from app.v1.users.router import v1_users_router

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict, None]:
    """Управление жизненным циклом приложения."""
    logger.info("Инициализация приложения...")

    if settings.MODE in ["PROD", "STAGE"]:
        sentry_sdk.init(
            dsn="https://44123996ba5b9e090680074bf6925991@o4506274465972224.ingest.us.sentry.io/4509603417227264",
            # Add data like request headers and IP for users,
            # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
            send_default_pii=True,
        )

    YookassaConfiguration.configure(
        account_id=settings.YOOKASSA_TEST_SHOP_ID,
        secret_key=settings.YOOKASSA_TEST_SECRET_KEY,
    )

    create_admin_panel(app)

    yield
    logger.info("Завершение работы приложения...")


def create_app() -> FastAPI:
    app = FastAPI(
        title=f"Садака_app ({settings.MODE})",
        lifespan=lifespan,
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # включаем middleware
    app.add_middleware(TimingMiddleware)

    # включаем логирование SQL и пула
    setup_sql_logging(engine)
    setup_pool_logging(engine)

    # Монтирование статических файлов
    # app.mount(
    #     '/static',
    #     StaticFiles(directory='app/static'),
    #     name='static'
    # )

    # Регистрация роутеров
    register_routers(app)

    return app


def register_routers(app: FastAPI) -> None:
    app.include_router(v1_t_bank_router_2, prefix="/app/v1/payments/t_bank", tags=["Payments t_bank v1"])
    app.include_router(v1_auth_router, prefix="/app/v1/auth", tags=["Auth v1"])
    app.include_router(v1_auth_sms_router, prefix="/app/v1/auth/sms", tags=["Auth sms v1"])
    app.include_router(v2_auth_router, prefix="/app/v2/auth", tags=["Auth v2"])
    app.include_router(v1_google_router, prefix="/app/v1/google", tags=["Google OAuth v1"])
    app.include_router(v1_s3_router, prefix="/app/v1/s3_storage", tags=["S3 Storage v1"])
    app.include_router(v1_users_router, prefix="/app/v1/users", tags=["Users v1"])
    app.include_router(v1_projects_router, prefix="/app/v1/projects", tags=["Projects v1"])
    app.include_router(v1_funds_router, prefix="/app/v1/funds", tags=["Funds v1"])
    app.include_router(v1_cities_router, prefix="/app/v1/cities", tags=["Cities v1"])
    app.include_router(v1_comment_router, prefix="/app/v1/comments", tags=["Comments v1"])
    app.include_router(v1_rating_router, prefix="/app/v1/ratings", tags=["Ratings v1"])
    app.include_router(v1_referral_router, prefix="/app/v1/referral", tags=["Referral v1"])

    # Payments
    app.include_router(v1_payments_core_router, prefix="/app/v1/payments", tags=["Payments v1"])
    app.include_router(v1_yookassa_router, prefix="/app/v1/payments/yookassa", tags=["Payments yookassa v1"])


# Создание экземпляра приложения
app = create_app()
