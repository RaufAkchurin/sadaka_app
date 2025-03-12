import datetime

import pytest
from pydantic import EmailStr

from app.auth.dao import UsersDAO
from app.auth.models import User
from app.auth.schemas import EmailModel, SUserAuth, SUserAddDB
from app.auth.utils import create_tokens, authenticate_user, get_password_hash
from jose import jwt

from app.config import settings


@pytest.mark.parametrize("user_id", ['123', '456'])
async def test_create_token_success(user_id):
    # Данные для теста
    data = {"sub": user_id}

    # Создание токенов
    new_tokens = create_tokens(data)

    # Проверка, что токены были созданы
    assert new_tokens.get('access_token')
    assert new_tokens.get('refresh_token')

    now = datetime.datetime.now(datetime.timezone.utc)

    # Проверка времени истечения токенов
    access_expire = now + datetime.timedelta(seconds=10)
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

async def test_authenticate_user(session):
    users_dao = UsersDAO(session)
    hash = get_password_hash("12345")
    user_data_dict = {"email": "test12@test.com",
                      "phone_number": "+74444444499",
                      "first_name": "test12",
                      "last_name": "test12",
                      "password": hash}

    user_dao = UsersDAO(session)
    new_user = await user_dao.add(values=SUserAddDB(**user_data_dict))
    user = await users_dao.find_one_or_none(
        filters=EmailModel(email="test12@test.com")
    )

    authenticated = await authenticate_user(user=user, password="12345")
    assert isinstance(authenticated, User)

    authenticated = await authenticate_user(user=user, password="1234")
    assert authenticated is None