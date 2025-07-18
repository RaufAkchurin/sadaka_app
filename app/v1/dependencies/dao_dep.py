from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.v1.dao.database import async_session_maker


async def get_session_with_commit() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронная сессия с автоматическим коммитом."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_session_with_commit_cm():
    gen = get_session_with_commit()
    session = await gen.__anext__()
    try:
        yield session
    finally:
        await gen.aclose()


async def get_session_without_commit() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронная сессия без автоматического коммита."""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
