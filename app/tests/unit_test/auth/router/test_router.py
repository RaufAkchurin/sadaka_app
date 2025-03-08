import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

async def test_all_users_unauthorized():
    async with AsyncClient(transport=ASGITransport(app),
                           base_url="http://test/auth") as client:
        response = await client.get("/all_users/")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

async def test_all_users_not_admin():
    pass


async def test_refresh_token_invalid():
    async with AsyncClient(transport=ASGITransport(app),
                           base_url="http://test/auth") as client:
        response = await client.post("/refresh")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

async def test_logout_without_auth():
    async with AsyncClient(transport=ASGITransport(app),
                           base_url="http://test/auth") as client:
        response = await client.post("/logout")
        assert response.status_code == 200
        assert response.json() == {"message": "Пользователь успешно вышел из системы"}
        # Проверяем, что куки удалены
        assert "user_access_token" not in response.cookies
        assert "user_refresh_token" not in response.cookies

