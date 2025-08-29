import subprocess
from pathlib import Path

import httpx
import pytest
from httpx import ASGITransport, AsyncClient
from main import app as fastapi_app
from sqlalchemy import text
from yookassa import Configuration

from app.models.user import User
from app.settings import settings
from app.tests.schemas import AuthorizedClientModel, CookiesModel
from app.utils.scripts.local_db_fill import prepare_database_core
from app.v1.dao.database import async_session_maker, Base, engine
from app.v1.users.dao import CommentDAO, OneTimePassDAO, UserDAO

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # sadaka_app/

import pytest


def apply_migration():
    subprocess.run("alembic upgrade head", shell=True, check=True, cwd=PROJECT_ROOT)
    print("✅ Миграции применены.")

async def reset_database():
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
    subprocess.run("alembic upgrade head", shell=True, check=True, cwd=PROJECT_ROOT)



@pytest.fixture(autouse=True)
def setup_yookassa_config():
    Configuration.account_id = settings.YOOKASSA_TEST_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_TEST_SECRET_KEY

# --- готовим БД один раз перед всеми тестами ---
@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    await reset_database()
    async with async_session_maker() as session_new:
        assert settings.MODE == "TEST"
        await prepare_database_core(session_new)
        await session_new.commit()

# --- каждая функция теста получает свою сессию ---
@pytest.fixture(scope="function")
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
async def user_dao(session) -> UserDAO:
    user_dao = UserDAO(session)
    return user_dao


@pytest.fixture(scope="function")
async def otp_dao(session) -> OneTimePassDAO:
    otp_dao = OneTimePassDAO(session)
    return otp_dao


@pytest.fixture(scope="function")
async def comment_dao(session) -> CommentDAO:
    comment_dao = CommentDAO(session)
    return comment_dao


@pytest.fixture(scope="function")
async def ac():
    async with AsyncClient(transport=ASGITransport(fastapi_app), base_url="http://test/") as async_client:
        yield async_client


@pytest.fixture(scope="function")
async def auth_ac():
    async with AsyncClient(transport=ASGITransport(fastapi_app), base_url="http://test") as ac:
        await ac.post("/app/v1/auth/login/", json={"email": "user1@test.com", "password": "password"})
        assert ac.cookies["user_access_token"]

        yield AuthorizedClientModel(
            client=ac,
            cookies=CookiesModel(
                user_access_token=ac.cookies.get("user_access_token"),
                user_refresh_token=ac.cookies.get("user_refresh_token"),
            ),
        )


@pytest.fixture(scope="class")
async def authenticated_super():
    async with AsyncClient(transport=ASGITransport(fastapi_app), base_url="http://test") as ac:
        response = await ac.post(
            "/app/v1/auth/login/",
            json={"email": "superadmin@test.com", "password": "password"},
        )
        assert response.status_code == 200
        assert ac.cookies["user_access_token"]

        yield AuthorizedClientModel(
            client=ac,
            cookies=CookiesModel(
                user_access_token=ac.cookies.get("user_access_token"),
                user_refresh_token=ac.cookies.get("user_refresh_token"),
            ),
        )


async def auth_by(ac: AsyncClient, user: User):
    logout_response = await ac.post("/app/v1/auth/logout/")
    assert logout_response.status_code == 307

    login_response = await ac.post("/app/v1/auth/login/", json={"email": user.email, "password": "password"})
    assert login_response.status_code == 200
    assert isinstance(ac.cookies, httpx.Cookies)
    return AuthorizedClientModel(
        client=ac,
        cookies=CookiesModel(
            user_access_token=ac.cookies.get("user_access_token"),
            user_refresh_token=ac.cookies.get("user_refresh_token"),
        ),
    )
