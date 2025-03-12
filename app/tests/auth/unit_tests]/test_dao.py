from app.auth.dao import UsersDAO
from app.auth.schemas import SUserRegister, SUserAddDB, EmailModel


async def test_add_user_and_find_by_id(session):
    user_data_dict = {"email": "1test@test.com",
                     "phone_number": "+74444444499",
                     "first_name": "test",
                     "last_name": "test",
                     "password": "8654567"}

    user_dao = UsersDAO(session)
    new_user = await user_dao.add(values=SUserAddDB(**user_data_dict))
    assert new_user.id == 8

    user = await user_dao.find_one_or_none_by_id(new_user.id)
    assert user.email == "1test@test.com"


async def test_find_one_or_none(session):
    user_dao = UsersDAO(session)
    user_data_dict = {"email": "2test@test.com",
                     "phone_number": "+74444444498",
                     "first_name": "test4",
                     "last_name": "test4",
                     "password": "8654567"}

    await user_dao.add(values=SUserAddDB(**user_data_dict))
    user = await user_dao.find_one_or_none(filters=EmailModel(email="2test@test.com"))
    assert user.first_name == "test4"

    user = await user_dao.find_one_or_none(filters=EmailModel(email="nonexistent@test.com"))
    assert user is None
#TODO add roles

async def test_find_all(session):
    user_dao = UsersDAO(session)
    users = await user_dao.find_all()
    assert len(users) == 9