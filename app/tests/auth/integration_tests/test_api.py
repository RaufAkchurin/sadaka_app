import pytest
from app.tests.conftest import async_client


@pytest.mark.parametrize("email, phone_number, first_name, last_name, password, confirm_password, status_code, response_message",
[
    ("user@example.com", "+79179876622", "string", "string", "password", "password", 200, {'message': 'Вы успешно зарегистрированы!'}),
    ("user@example.com", "+79179876622", "string", "string", "password", "password", 409, {'detail': 'Пользователь уже существует'}),
    ("user@example.com", "+791", "string", "string", "password", "password", 422, None), #phone number validation
    ("user@example.com", "+79179876622", "string", "string", "password", "password1", 422, None), #password confirm validation
    ("abcde", "+79179876625", "string", "string", "password", "password", 422, None), #email validation
]
)
async def test_register(async_client, email, phone_number, first_name, last_name, password, confirm_password, status_code, response_message):
    # Сначала регистрируем пользователя
    user_data = {"email": email, "phone_number": phone_number, "first_name": first_name,
                 "last_name": last_name, "password": password, "confirm_password": confirm_password}
    response = await async_client.post("/auth/register/", json=user_data)
    assert response.status_code == status_code
    if response_message:
        assert response.json() == response_message



@pytest.mark.parametrize("email, password, status_code, response_message",
 [
     ("test1@test.com", "wrong_password", 400, {'detail': 'Неверная почта или пароль'}),
     ("test1@test.com", "password", 200, {"ok":True,"message":"Авторизация успешна!"}),
  ])
async def test_login(async_client, email, password, status_code, response_message):
    user_data = {"email": email, "password": password}
    response = await async_client.post("/auth/login/", json=user_data)
    assert response.status_code == status_code
    if response_message:
        assert response.json() == response_message

    if status_code == 200:
        assert response.cookies.get('user_access_token')
        assert response.cookies.get('user_refresh_token')



async def test_me_400(self):
    async with AsyncClient(transport=ASGITransport(app),
                           base_url="http://test/auth",
                           ) as client:
        response = await client.get("/me/")
        assert response.status_code == 400
        assert response.json() == {'detail': 'Токен отсутствует в заголовке'}

async def test_root(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {'author': 'Яковенко Алексей', 'community': 'https://t.me/PythonPathMaster',
                               'message': "Добро пожаловать! Проект создан для сообщества 'Легкий путь в Python'."}


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

