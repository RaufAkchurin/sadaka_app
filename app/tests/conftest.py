import pytest
from httpx import ASGITransport, AsyncClient
from main import app as fastapi_app  # noqa
from sqlalchemy import event
from sqlalchemy.engine import Engine
from tests.fixtures.auth import *  # noqa
from tests.fixtures.dao import *  # noqa
from utils.scripts.local_db_fill import prepare_database_core  # noqa
from yookassa import Configuration

from app.settings import settings
from app.v1.dao.database import async_session_maker


@pytest.fixture
def query_counter():
    queries = []

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        queries.append(statement)

    event.listen(Engine, "before_cursor_execute", before_cursor_execute)

    yield queries  # отдаём список запросов в тест

    event.remove(Engine, "before_cursor_execute", before_cursor_execute)


@pytest.fixture(autouse=True)
def setup_yookassa_config():
    Configuration.account_id = settings.YOOKASSA_TEST_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_TEST_SECRET_KEY


@pytest.fixture(scope="class", autouse=True)
async def prepare_database(session):
    assert settings.MODE == "TEST"
    await prepare_database_core(session)


@pytest.fixture(scope="class")
async def prepare_database_manually(session):
    await prepare_database_core(session)


@pytest.fixture(scope="class")
async def session():
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture(scope="class")
async def ac():
    async with AsyncClient(transport=ASGITransport(fastapi_app), base_url="http://test/") as async_client:
        yield async_client
