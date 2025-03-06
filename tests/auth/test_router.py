import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app),
                           base_url="http://test/") as client:
        response = await client.get("/")

        assert response.status_code == 200
        assert response.json() == {'author': 'Яковенко Алексей', 'community': 'https://t.me/PythonPathMaster',
                            'message': "Добро пожаловать! Проект создан для сообщества 'Легкий путь в Python'."}

@pytest.mark.asyncio
async def test_me_400():
    async with AsyncClient(transport=ASGITransport(app),
                           base_url="http://test/auth",
                           ) as client:
        response = await client.get("/me/")
        assert response.status_code == 400
        assert response.json() == {'detail': 'Токен отсутствует в заголовке'}

@pytest.mark.asyncio
async def test_register_existing_user():
    async with AsyncClient(transport=ASGITransport(app),
                           base_url="http://test/auth") as client:
        # Сначала регистрируем пользователя
        user_data = {
            "email": "test@example.com",
            "password": "testpassword",
            "confirm_password": "testpassword"
        }
        await client.post("/register/", json=user_data)
        
        # Пытаемся зарегистрировать того же пользователя снова
        response = await client.post("/register/", json=user_data)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_me_unauthorized():
    async with AsyncClient(transport=ASGITransport(app),
                           base_url="http://test/auth") as client:
        response = await client.get("/me/")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

@pytest.mark.asyncio
async def test_all_users_unauthorized():
    async with AsyncClient(transport=ASGITransport(app),
                           base_url="http://test/auth") as client:
        response = await client.get("/all_users/")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

@pytest.mark.asyncio
async def test_all_users_not_admin():
    pass


@pytest.mark.asyncio
async def test_refresh_token_invalid():
    async with AsyncClient(transport=ASGITransport(app),
                           base_url="http://test/auth") as client:
        response = await client.post("/refresh")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

@pytest.mark.asyncio
async def test_logout_without_auth():
    async with AsyncClient(transport=ASGITransport(app),
                           base_url="http://test/auth") as client:
        response = await client.post("/logout")
        assert response.status_code == 200
        assert response.json() == {"message": "Пользователь успешно вышел из системы"}
        # Проверяем, что куки удалены
        assert "user_access_token" not in response.cookies
        assert "user_refresh_token" not in response.cookies