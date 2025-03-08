from httpx import AsyncClient, ASGITransport
from app.main import app
from app.tests.conftest import async_client


class TestRegisterEndpoint:
    async def test_register_new_user(self, async_client):
        async with AsyncClient(transport=ASGITransport(app),
                               base_url="http://test/auth") as client:
            # Сначала регистрируем пользователя
            user_data = {
                "email": "user@example.com",
                "phone_number": "+79179876622",
                "first_name": "string",
                "last_name": "string",
                "password": "string",
                "confirm_password": "string"
            }
            response = await client.post("/register/", json=user_data)
            assert response.status_code == 200
            assert response.json() == {'message': 'Вы успешно зарегистрированы!'}

    async def test_register_existing_user(self):
        async with AsyncClient(transport=ASGITransport(app),
                               base_url="http://test/auth") as client:
            # Сначала регистрируем пользователя
            user_data = {
                "email": "user@example.com",
                "phone_number": "+79179876622",
                "first_name": "string",
                "last_name": "string",
                "password": "string",
                "confirm_password": "string"
            }
            await client.post("/register/", json=user_data)

            # Пытаемся зарегистрировать того же пользователя снова
            response = await client.post("/register/", json=user_data)
            assert response.status_code == 409
            assert response.json() == {'detail': 'Пользователь уже существует'}

    async def test_register_phone_validation(self):
        async with AsyncClient(transport=ASGITransport(app),
                               base_url="http://test/auth") as client:
            # Сначала регистрируем пользователя
            user_data = {
                "email": "user@example.com",
                "phone_number": "+987",
                "first_name": "string",
                "last_name": "string",
                "password": "string",
                "confirm_password": "string"
            }
            await client.post("/register/", json=user_data)

            # Пытаемся зарегистрировать того же пользователя снова
            response = await client.post("/register/", json=user_data)
            assert response.status_code == 422
            assert response.json().get("detail")[0].get("msg") == ('Value error, Номер телефона должен начинаться с'
                                                                   ' "+" и содержать от 5 до 15 цифр')

    async def test_register_pass_validation(self):
        async with AsyncClient(transport=ASGITransport(app),
                               base_url="http://test/auth") as client:
            # Сначала регистрируем пользователя
            user_data = {
                "email": "user@example.com",
                "phone_number": "+79878765522",
                "first_name": "string",
                "last_name": "string",
                "password": "string",
                "confirm_password": "string1"
            }
            await client.post("/register/", json=user_data)

            # Пытаемся зарегистрировать того же пользователя снова
            response = await client.post("/register/", json=user_data)
            assert response.status_code == 422
            assert response.json().get("detail")[0].get("msg") == 'Value error, Пароли не совпадают'