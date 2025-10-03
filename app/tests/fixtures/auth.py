import httpx
import pytest
from httpx import ASGITransport, AsyncClient
from main import app as fastapi_app

from app.models.user import User
from app.tests.schemas import AuthorizedClientModel, CookiesModel


@pytest.fixture(scope="class")
async def auth_ac_super():
    async with AsyncClient(transport=ASGITransport(fastapi_app), base_url="http://test") as ac:
        await ac.post("/app/v1/auth/login/", json={"email": "superadmin@test.com", "password": "password"})
        assert ac.cookies["user_access_token"]

        yield AuthorizedClientModel(
            client=ac,
            cookies=CookiesModel(
                user_access_token=ac.cookies.get("user_access_token"),
                user_refresh_token=ac.cookies.get("user_refresh_token"),
            ),
        )


@pytest.fixture(scope="class")
async def auth_ac_admin():
    async with AsyncClient(transport=ASGITransport(fastapi_app), base_url="http://test") as ac:
        await ac.post("/app/v1/auth/login/", json={"email": "admin@test.com", "password": "password"})
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
