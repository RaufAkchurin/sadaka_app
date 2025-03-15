import asyncio
import json
import os

import httpx
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import insert
from app.auth.dao import UsersDAO
from app.config import settings
from app.dao.database import async_session_maker, engine, Base
from app.auth.models import User, Role
from app.main import app as fastapi_app
from app.tests.schemas import AuthorizedClientModel, CookiesModel


@pytest.fixture(scope="class")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

def open_mock_json(model: str):
    test_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(test_dir, f"tests/mock_{model}.json")
    with open(file_path, "r") as file:
        return json.load(file)


async def prepare_database_core(session):
    try:
        assert settings.MODE == "TEST"
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        users = open_mock_json("user")
        roles = open_mock_json("role")

        async with async_session_maker() as session:
            add_users = insert(User).values(users)
            add_roles = insert(Role).values(roles)
            await session.execute(add_users)
            await session.execute(add_roles)
            await session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

@pytest.fixture(scope='class', autouse=True)
async def prepare_database(session):
    await prepare_database_core(session)

@pytest.fixture(scope='class')
async def prepare_database_manually(session):
    await prepare_database_core(session)


@pytest.fixture(scope="class")
async def session():
    async with async_session_maker() as session:
        yield session

@pytest.fixture(scope="class")
async def user_dao(session) -> UsersDAO:
    user_dao = UsersDAO(session)
    return user_dao

@pytest.fixture(scope="class")
async def ac():
    async with AsyncClient(transport=ASGITransport(fastapi_app),
                           base_url="http://test/") as async_client:
        yield async_client


@pytest.fixture(scope="class")
async def authenticated_ac():
    async with AsyncClient(transport=ASGITransport(fastapi_app),
                           base_url="http://test") as ac:
        await ac.post("/auth/login/", json={"email": "user1@test.com", "password": "password"})
        assert ac.cookies["user_access_token"]
        tokens ={"user_access_token": ac.cookies.get('user_access_token'),
                "user_refresh_token": ac.cookies.get('user_refresh_token')}
        yield ac, tokens

@pytest.fixture(scope="class")
async def authenticated_super():
    async with AsyncClient(transport=ASGITransport(fastapi_app),
                           base_url="http://test") as ac:
        response = await ac.post("/auth/login/", json={"email": "superadmin@test.com", "password": "password"})
        assert response.status_code == 200
        assert ac.cookies["user_access_token"]
        tokens ={"user_access_token": ac.cookies.get('user_access_token'),
                "user_refresh_token": ac.cookies.get('user_refresh_token')}
        yield ac, tokens


async def authorize_by(ac: AsyncClient, user: User):
    logout_response = await ac.post("/auth/logout/")
    assert logout_response.status_code == 307

    login_response = await ac.post("/auth/login/", json={"email": user.email, "password": "password"})
    assert login_response.status_code == 200
    assert isinstance(ac.cookies, httpx.Cookies)
    return AuthorizedClientModel(client=ac, cookies=CookiesModel(user_access_token=ac.cookies.get('user_access_token'),
                                                                 user_refresh_token=ac.cookies.get('user_refresh_token')))