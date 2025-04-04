import datetime
import pytest

from app.users.models import User
from app.users.schemas import EmailModel, SUserAddDB
from app.auth.service_auth import create_tokens, authenticate_user
from jose import jwt

from app.auth.service_jwt import get_password_hash
from app.settings import settings

class TestUtils:
    @pytest.mark.parametrize("user_id", ['123', '456'])
    async def test_create_token_success(self, user_id):
        # Данные для теста
        data = {"sub": user_id}

        # Создание токенов
        new_tokens = create_tokens(data)

        # Проверка, что токены были созданы
        assert new_tokens.get('access_token')
        assert new_tokens.get('refresh_token')

        now = datetime.datetime.now(datetime.timezone.utc)

        # Проверка времени истечения токенов
        access_expire = now + datetime.timedelta(minutes=60)
        refresh_expire = now + datetime.timedelta(days=7)

        # Декодируем access_token и проверяем его содержимое
        decoded_sub = jwt.decode(new_tokens.get('access_token'), settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded_sub['sub'] == user_id
        assert decoded_sub['type'] == 'access'
        assert decoded_sub['exp'] == int(access_expire.timestamp())

        # Декодируем refresh_token и проверяем его содержимое
        decoded_refresh = jwt.decode(new_tokens.get('refresh_token'), settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded_refresh['sub'] == user_id
        assert decoded_refresh['type'] == 'refresh'
        assert decoded_refresh['exp'] == int(refresh_expire.timestamp())

    async def test_authenticate_user(self, user_dao):
        hash = get_password_hash("12345")
        user_data_dict = {"email": "test12@test.com",
                          "name": "test12",
                          "password": hash}

        await user_dao.add(values=SUserAddDB(**user_data_dict, is_active=True))
        user = await user_dao.find_one_or_none(
            filters=EmailModel(email="test12@test.com")
        )

        authenticated = await authenticate_user(user=user, password="12345")
        assert isinstance(authenticated, User)

        authenticated = await authenticate_user(user=user, password="1234")
        assert authenticated is None