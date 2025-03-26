import pytest

from app.tests.conftest import authorize_by
from app.users.schemas import EmailModel

class TestUsers:
    @pytest.mark.parametrize("is_authorized, status_code, response_message",
                             [
                                 (True, 200, {'city_id': 1,
                                              'city_name': 'Kazan',
                                              'email': 'user1@test.com',
                                              'id': 4,
                                              'is_anonymous': False,
                                              'name': 'user1',
                                              'picture': None,
                                              'role_id': 1,
                                              'role_name': 'user'}),
                                 (False, 400, {"detail": "Токен отсутствует в заголовке"}),
                             ])
    async def test_me_200(self, ac, authenticated_ac, is_authorized, status_code, response_message):
        if is_authorized:
            response = await authenticated_ac.client.get("/users/me/", cookies=authenticated_ac.cookies.dict())

        else:
            response = await ac.get("/users/me/")

        assert response.status_code == status_code
        assert response.json() == response_message


    @pytest.mark.usefixtures("prepare_database_manually")
    @pytest.mark.parametrize("email, status_code, users_count, response_message",
     [   #AUTHORIZED USERS
         ("superadmin@test.com", 200, 5,    None),
         ("admin@test.com",      200, 5,    None),
         ("moderator@test.com",  403, None, {'detail': 'Недостаточно прав'}),
         ("user1@test.com",      403, None, {'detail': 'Недостаточно прав'}),
         # NOT AUTHORIZED USERS
         (None,                  400, None, {"detail":"Токен отсутствует в заголовке"} ),
     ])
    async def test_all_users(self, ac, user_dao, email, status_code, users_count, response_message):
        if email:
            current_user = await user_dao.find_one_or_none(filters=EmailModel(email=email))
            if current_user is None:
                raise ValueError("User not found")
            authorized_client = await authorize_by(ac, current_user)
            client = authorized_client.client
            response = await client.get("/users/all_users/", cookies=authorized_client.cookies.dict())
        else:
            response = await ac.get("/users/all_users/")

        assert response.status_code == status_code
        if users_count:
            assert len(response.json()) == users_count
        if response_message:
            assert response.json() == response_message


    async def test_update_user(self, authenticated_ac):
        new_data = {
            'body':{
                    "email": "updated@example.com",
                    "name": "updated",
                    "picture": "updated",
                    "city_id": 2
        }}

        response = await authenticated_ac.client.post("/users/update/",
                                                      cookies=authenticated_ac.cookies.dict(),
                                                      data = new_data
                                                      )
        assert response.status_code == 200