import pytest
from app.auth.schemas import EmailModel
from app.tests.conftest import ac, authenticated_ac, authorize_by


class TestApi:
    async def test_root(self, ac):
        response = await ac.get("/")
        assert response.status_code == 200
        assert response.json() == {'author': 'Яковенко Алексей', 'community': 'https://t.me/PythonPathMaster',
                                   'message': "Добро пожаловать! Проект создан для сообщества 'Легкий путь в Python'."}


    @pytest.mark.parametrize("email, phone_number, first_name, last_name, password, confirm_password, status_code, response_message",
    [
        ("user@example.com", "+79179876622", "string", "string", "password", "password", 200, {'message': 'Вы успешно зарегистрированы!'}),
        ("user@example.com", "+79179876622", "string", "string", "password", "password", 409, {'detail': 'Пользователь уже существует'}),
        ("user@example.com", "+791", "string", "string", "password", "password", 422, None), #phone number validation
        ("user@example.com", "+79179876622", "string", "string", "password", "password1", 422, None), #password confirm validation
        ("abcde", "+79179876625", "string", "string", "password", "password", 422, None), #email validation
    ]
    )
    async def test_register(self, ac, email, phone_number, first_name, last_name, password, confirm_password, status_code, response_message):
        # Сначала регистрируем пользователя
        user_data = {
                    "email": email,
                     "phone_number": phone_number,
                     "first_name": first_name,
                     "last_name": last_name,
                     "password": password,
                     "confirm_password": confirm_password
                     }
        response = await ac.post("/auth/register/", json=user_data)
        assert response.status_code == status_code
        if response_message:
            assert response.json() == response_message


    @pytest.mark.parametrize("email, password, status_code, response_message",
     [
         ("user1@test.com", "wrong_password", 400, {'detail': 'Неверная почта или пароль'}),
         ("user1@test.com", "password", 200, {"ok":True,"message":"Авторизация успешна!"}),
      ])
    async def test_login(self, ac, email, password, status_code, response_message):
        user_data = {"email": email, "password": password}
        response = await ac.post("/auth/login/", json=user_data)
        assert response.status_code == status_code
        if response_message:
            assert response.json() == response_message

        if status_code == 200:
            assert response.cookies.get('user_access_token')
            assert response.cookies.get('user_refresh_token')


    async def test_logout(self, authenticated_ac):
        authenticated_ac, cookies_with_tokens = authenticated_ac

        user_access_token = authenticated_ac.cookies.get('user_access_token')
        user_refresh_token = authenticated_ac.cookies.get('user_refresh_token')
        assert user_access_token is not None
        assert user_refresh_token is not None

        response = await authenticated_ac.post("/auth/logout")
        assert response.status_code == 200
        assert response.json() == {"message": "Пользователь успешно вышел из системы"}

        user_access_token = authenticated_ac.cookies.get('user_access_token')
        user_refresh_token = authenticated_ac.cookies.get('user_refresh_token')
        assert user_access_token is None
        assert user_refresh_token is None

    @pytest.mark.parametrize("is_authorized, status_code, response_message",
     [
         (True, 200, {'email': 'user1@test.com', 'first_name': 'user1', 'id': 4, 'last_name': 'user1',
                      'phone_number': '+71111111111','role_id': 1, 'role_name': 'user'}),
         (False, 400, {"detail": "Токен отсутствует в заголовке"}),
     ])

    async def test_me_200(self, ac, authenticated_ac, is_authorized, status_code, response_message):
        if is_authorized:
            authenticated_ac, cookies_with_tokens = authenticated_ac
            response = await authenticated_ac.get("/auth/me/", cookies=cookies_with_tokens)

        else:
            response = await ac.get("/auth/me/")

        assert response.status_code == status_code
        assert response.json() == response_message


    @pytest.mark.parametrize("is_authorized, status_code, response_message",
     [
         (True, 200, {"message": "Токены успешно обновлены"}),
         (False, 400, {"detail": "Токен отсутствует в заголовке"}),
     ])
    async def test_refresh_token(self, ac, authenticated_ac, is_authorized, status_code, response_message):
            if is_authorized:
                client = authenticated_ac[0]
                response = await client.post("/auth/refresh", cookies=authenticated_ac[1])

            else:
                client = ac
                response = await client.post("/auth/refresh")

            assert response.status_code == status_code
            assert response.json() == response_message


    @pytest.mark.parametrize("role, is_authorized, status_code, users_count, response_message",
     [   #AUTHORIZED USERS
         ("superadmin@test.com",  True, 200, 6,    None),
         ("admin@test.com",       True, 200, 6,    None),
         ("moderator@test.com",   True, 403, None,    {'detail': 'Недостаточно прав'}),
         ("user1@test.com",        True, 403, None,    {'detail': 'Недостаточно прав'}),
         # NOT AUTHORIZED USERS
         (None, False, 400, None, {"detail":"Токен отсутствует в заголовке"} ),
     ])
    async def test_all_users(self, ac,authenticated_super, user_dao,role, is_authorized, status_code, users_count, response_message):
        if is_authorized:
            current_user = await user_dao.find_one_or_none(filters=EmailModel(email=role))
            if current_user is None:
                raise ValueError("User not found")
            authorized_client = await authorize_by(ac, current_user)
            client = authorized_client.client

            response = await client.get("/auth/all_users/", cookies=authorized_client.cookies.dict())

            assert response.status_code == status_code

            if users_count:
                assert len(response.json()) == users_count

            if response_message:
                assert response.json() == response_message
