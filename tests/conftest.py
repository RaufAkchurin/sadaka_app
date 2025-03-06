# import asyncio
# from typing import AsyncGenerator
#
# import pytest
# import pytest_asyncio
# from sqlalchemy.sql import text
# from sqlalchemy.ext.asyncio import (
#     AsyncSession,
#     async_sessionmaker,
#     create_async_engine,
# )
#
#
# from app.dao.database import Base
# from app.config import settings
#
# pytest_plugins = [
#     # "tests.fixtures.client_sessions",
#     # "tests.fixtures.data",
#     # "tests.fixtures.repositories_services",
# ]
#
# test_engine = create_async_engine(settings.DATABASE_URL)
# test_async_session_maker = async_sessionmaker(
#     test_engine,
#     expire_on_commit=False,
#     class_=AsyncSession,
# )
#
#
# @pytest.fixture(scope="session")
# def event_loop():
#     policy = asyncio.get_event_loop_policy()
#     loop = policy.new_event_loop()
#     yield loop
#     loop.close()
#
#
# @pytest.fixture(scope="session", autouse=True)
# async def async_db_engine():
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
#     yield test_engine
#
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#
#
# @pytest_asyncio.fixture()
# async def db_session() -> AsyncGenerator[AsyncSession, None]:
#     async with test_async_session_maker() as session:
#         try:
#             yield session
#         except Exception:
#             await session.rollback()
#             raise
#         finally:
#             for table in reversed(Base.metadata.sorted_tables):
#                 await session.execute(text(f"TRUNCATE {table.name} CASCADE;"))
#                 await session.commit()