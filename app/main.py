import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from admin.register import create_admin_panel
from app.auth.v1.router import v1_auth_router, v2_auth_router
from app.auth_google.v1.router import v1_google_router
from app.project.v1.router import v1_projects_router
from app.s3_storage.v1.router import v1_s3_router
from app.users.v1.router import v1_users_router

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict, None]:
    """Управление жизненным циклом приложения."""
    logger.info("Инициализация приложения...")

    create_admin_panel(app)

    yield
    logger.info("Завершение работы приложения...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Садака_app",
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
    app.include_router(v1_auth_router, prefix="/app/v1/auth", tags=["Auth v1"])
    app.include_router(v2_auth_router, prefix="/app/v2/auth", tags=["Auth v2"])
    app.include_router(v1_google_router, prefix="/app/v1/google", tags=["Google OAuth"])
    app.include_router(v1_s3_router, prefix="/app/v1/s3_storage", tags=["S3 Storage"])
    app.include_router(v1_users_router, prefix="/app/v1/users", tags=["Users"])
    app.include_router(v1_projects_router, prefix="/app/v1/projects", tags=["Projects"])


# Создание экземпляра приложения
app = create_app()
