from pydantic import EmailStr

from app.auth.dao import UsersDAO
from app.auth.schemas import SUserRegister, SUserAddDB


async def test_add_and_get_new_user(session):
    user_dao = UsersDAO(session)
    user_data = {
        "phone_number": "+79179876621",
        "first_name": "first_name",
        "last_name": "last_name",
        "email": "test6@test.com",
        "password": "password",
        }

    # Добавление пользователя
    new_user = await user_dao.add(values=SUserAddDB(**user_data))
    assert new_user.id == 6
    assert new_user is not None
