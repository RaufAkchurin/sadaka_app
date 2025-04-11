import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.auth.google.router import google_router
from app.auth.router import auth_router
from app.s3_storage.router import s3_router
from app.users.router import users_router

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict, None]:
    """Управление жизненным циклом приложения."""
    logger.info("Инициализация приложения...")
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
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(google_router, prefix="/google", tags=["Google OAuth"])
    app.include_router(users_router, prefix="/users", tags=["Users"])
    app.include_router(s3_router, prefix="/s3_storage", tags=["S3 Storage"])


# Создание экземпляра приложения
app = create_app()
