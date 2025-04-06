import json
import os
import httpx
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import insert
from app.geo.models import Country, Region, City
from app.users.dao import UsersDAO
from app.settings import settings
from app.dao.database import async_session_maker, engine, Base
from app.main import app as fastapi_app
from app.tests.schemas import AuthorizedClientModel, CookiesModel
from app.users.models import User, Role

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

        country = open_mock_json("country")
        region = open_mock_json("region")
        city = open_mock_json("city")
        users = open_mock_json("user")
        roles = open_mock_json("role")

        async with async_session_maker() as session:
            add_country = insert(Country).values(country)
            add_region = insert(Region).values(region)
            add_city = insert(City).values(city)
            add_users = insert(User).values(users)
            add_roles = insert(Role).values(roles)

            await session.execute(add_country)
            await session.execute(add_region)
            await session.execute(add_city)
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
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@pytest.fixture(scope="function")
async def user_dao(session) -> UsersDAO:
    user_dao = UsersDAO(session)
    return user_dao

@pytest.fixture(scope="class")
async def ac():
    async with AsyncClient(transport=ASGITransport(fastapi_app),
                           base_url="http://test/") as async_client:
        yield async_client


@pytest.fixture(scope="class")
async def auth_ac():
    async with AsyncClient(transport=ASGITransport(fastapi_app),
                           base_url="http://test") as ac:
        await ac.post("/auth/login/", json={"email": "user1@test.com", "password": "password"})
        assert ac.cookies["user_access_token"]
        yield AuthorizedClientModel(client=ac, cookies=CookiesModel(user_access_token=ac.cookies.get('user_access_token'),
                                                                    user_refresh_token=ac.cookies.get('user_refresh_token')))


@pytest.fixture(scope="class")
async def authenticated_super():
    async with AsyncClient(transport=ASGITransport(fastapi_app),
                           base_url="http://test") as ac:
        response = await ac.post("/auth/login/", json={"email": "superadmin@test.com", "password": "password"})
        assert response.status_code == 200
        assert ac.cookies["user_access_token"]

        yield AuthorizedClientModel(client=ac, cookies=CookiesModel(user_access_token=ac.cookies.get('user_access_token'),
                                                                    user_refresh_token=ac.cookies.get('user_refresh_token')))


async def auth_by(ac: AsyncClient, user: User):
    logout_response = await ac.post("/auth/logout/")
    assert logout_response.status_code == 307

    login_response = await ac.post("/auth/login/", json={"email": user.email, "password": "password"})
    assert login_response.status_code == 200
    assert isinstance(ac.cookies, httpx.Cookies)
    return AuthorizedClientModel(client=ac, cookies=CookiesModel(user_access_token=ac.cookies.get('user_access_token'),
                                                                 user_refresh_token=ac.cookies.get('user_refresh_token')))