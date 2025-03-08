import asyncio
import json
import os

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from sqlalchemy import insert
from app.config import settings
from app.dao.database import async_session_maker, engine, Base
from app.auth.models import User
from app.main import app as fastapi_app



@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        test_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(test_dir, f"tests/mock_{model}.json")
        with open(file_path, "r") as file:
            return json.load(file)

    users = open_mock_json("user")

    async with async_session_maker() as session:
        add_users = insert(User).values(users)
        await session.execute(add_users)
        await session.commit()

    # Взято из документации к pytest-asyncio
@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def async_client():
    async with AsyncClient(transport=ASGITransport(fastapi_app),
                           base_url="http://test/") as async_client:
        yield async_client