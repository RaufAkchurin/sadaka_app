import httpx
import pytest
from httpx import ASGITransport, AsyncClient
from main import app as fastapi_app
from sqlalchemy import event
from sqlalchemy.engine import Engine
from tests.schemas import AuthorizedClientModel, CookiesModel
from utils.scripts.local_db_fill import prepare_database_core
from yookassa import Configuration

from app.models.user import User
from app.settings import settings
from app.v1.dao.database import async_session_maker
from app.v1.users.dao import CommentDAO, OneTimePassDAO, PaymentDAO, UserDAO


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
async def payment_dao(session) -> PaymentDAO:
    payment_dao = PaymentDAO(session)
    return payment_dao


@pytest.fixture(scope="class")
async def ac():
    async with AsyncClient(transport=ASGITransport(fastapi_app), base_url="http://test/") as async_client:
        yield async_client


@pytest.fixture(scope="class")
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
