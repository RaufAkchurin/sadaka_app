import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import TIMESTAMP, Integer, func, inspect
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from app.settings import settings

mode = settings.MODE

if settings.MODE in ["PROD", "STAGE"]:
    # Настройки для Production
    DB_DRIVER = "postgresql+asyncpg"
    DATABASE_URL = (
        f"{DB_DRIVER}://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB_NAME}"
    )
    DATABASE_PARAMS = {"pool_size": 5, "max_overflow": 10}

# ТЕСТ НА СКЛЛАЙТЕ ЛОКАЛЬНО

# elif settings.MODE == "TEST":
#     # Настройки для тестирования (in-memory SQLite)
#     DB_DRIVER = "sqlite+aiosqlite"
#     DATABASE_URL = f"{DB_DRIVER}:///:memory:"
#     DATABASE_PARAMS = {
#         "echo": True,
#         "poolclass": StaticPool,  # одно соединение на все тесты
#         "connect_args": {"check_same_thread": False},
#     }


# ТЕСТ на ПОСТГРЕС ОБЛАЧНОМ ТУДУ - ЗАМЕНИТЬ НА ДОКЕР ЛОКАЛЬНО
elif settings.MODE == "TEST":
    DB_DRIVER = "postgresql+asyncpg"
    DATABASE_URL = (
        f"{DB_DRIVER}://{settings.POSTGRES_TEST_USER}:{settings.POSTGRES_TEST_PASSWORD}"
        f"@{settings.POSTGRES_TEST_HOST}/{settings.POSTGRES_TEST_DB_NAME}"
    )
    DATABASE_PARAMS = {"pool_size": 5, "max_overflow": 10}

else:
    # Настройки по умолчанию
    # DB_DRIVER = "sqlite+aiosqlite"
    # DATABASE_URL = f"{DB_DRIVER}:///{settings.BASE_DIR}/data/db.sqlite3"
    # DATABASE_PARAMS = {}

    DB_DRIVER = "postgresql+asyncpg"
    DATABASE_URL = (
        f"{DB_DRIVER}://{settings.POSTGRES_TEST_USER}:{settings.POSTGRES_TEST_PASSWORD}"
        f"@{settings.POSTGRES_TEST_HOST}/{settings.POSTGRES_TEST_DB_NAME}"
    )
    DATABASE_PARAMS = {"pool_size": 5, "max_overflow": 10}

engine = create_async_engine(url=DATABASE_URL, **DATABASE_PARAMS)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

    def to_dict(self, exclude_none: bool = False):
        """
        Преобразует объект модели в словарь.

        Args:
            exclude_none (bool): Исключать ли None значения из результата

        Returns:
            dict: Словарь с данными объекта
        """
        result = {}
        for column in inspect(self.__class__).columns:
            value = getattr(self, column.key)

            # Преобразование специальных типов данных
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, uuid.UUID):
                value = str(value)

            # Добавляем значение в результат
            if not exclude_none or value is not None:
                result[column.key] = value

        return result

    def __repr__(self) -> str:
        """Строковое представление объекта для удобства отладки."""
        return f"<{self.__class__.__name__}(id={self.id}, created_at={self.created_at}, updated_at={self.updated_at})>"
