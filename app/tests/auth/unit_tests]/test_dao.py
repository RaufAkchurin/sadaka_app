from app.auth.schemas import SUserRegister, SUserAddDB, EmailModel
from app.tests.factory.factories_polyfactory import generate_phone_number, faker

class TestDAO:
    async def test_add_user_and_find_by_id(self, user_dao):
        user_data_dict = {"email": "1test@test.com",
                         "phone_number": "+74444444499",
                         "first_name": "test",
                         "last_name": "test",
                         "password": "8654567"}

        new_user = await user_dao.add(values=SUserAddDB(**user_data_dict))
        assert new_user.id == 6

        user = await user_dao.find_one_or_none_by_id(new_user.id)
        assert user.email == "1test@test.com"


    async def test_find_one_or_none(self, user_dao):
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

    async def test_find_all(self, user_dao):
        users = await user_dao.find_all()
        assert len(users) == 7

    async def test_add_many(self, user_dao):
        users = [
            {"email": faker.email(domain='test.com'),
             "phone_number": generate_phone_number(),
             "first_name": f"first name",
             "last_name": f"last name",
             "password": "8654567"}
            for i in range(10)
        ]

        new_users = await user_dao.add_many([SUserAddDB(**user_data) for user_data in users])
        assert len(new_users) == 10