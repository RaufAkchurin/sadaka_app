import pytest
from app.tests.conftest import auth_by
from app.users.schemas import EmailModel


class TestUsers:
    @pytest.mark.parametrize("is_authorized, status_code, response_message",
                             [
                                 (True, 200, {'city_id': 1,
                                             'city_name': 'Kazan',
                                             'email': 'user1@test.com',
                                             'id': 4,
                                             'is_active': True,
                                             'is_anonymous': False,
                                             'name': 'user1',
                                             'picture': None,
                                             'role_id': 1,
                                             'role_name': 'user'}),
                                 (False, 400, {"detail": "Токен отсутствует в заголовке"}),
                             ])
    async def test_me_200(self, ac, auth_ac, is_authorized, status_code, response_message):
        if is_authorized:
            response = await auth_ac.client.get("/users/me/", cookies=auth_ac.cookies.dict())

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
            authorized_client = await auth_by(ac, current_user)
            client = authorized_client.client
            response = await client.get("/users/all_users/", cookies=authorized_client.cookies.dict())
        else:
            response = await ac.get("/users/all_users/")

        assert response.status_code == status_code
        if users_count:
            assert len(response.json()) == users_count
        if response_message:
            assert response.json() == response_message


    @pytest.mark.parametrize("authorized, status_code, response_message",
     [   #AUTHORIZED USERS
         (True, 200, {'city_id': 1, 'email': 'updated@example.com', 'name': 'updated', 'picture': 'updated'}),
         (False, 400, {"detail":"Токен отсутствует в заголовке"}),
     ])
    async def test_update_user(self, ac, auth_ac, user_dao, authorized, status_code, response_message):
        new_data = {
            "email": "updated@example.com",
            "name": "updated",
            "picture": "updated",
            "city_id": 1
        }
        if authorized:
            response = await auth_ac.client.post(
                "/users/update/",
                cookies=auth_ac.cookies.dict(),
                json=new_data
            )

        else:
            response = await ac.post(
                "/users/update/",
                json=new_data
            )

        assert response.status_code == status_code
        assert response.json() == response_message


    async def test_delete_authorized_user(self, ac, auth_ac):
            me_response_before_deleting = await auth_ac.client.get("/users/me/", cookies=auth_ac.cookies.dict())
            assert me_response_before_deleting.status_code == 200
            assert me_response_before_deleting.json()['is_active'] == True

            response = await auth_ac.client.post("/users/delete/", cookies=auth_ac.cookies.dict(),)
            me_response = await auth_ac.client.get("/users/me/", cookies=auth_ac.cookies.dict())

            assert response.status_code == 200
            assert response.json() == {'message': 'Вы успешно удалили аккаунт!'}

            assert me_response.status_code == 200
            assert me_response.json()['is_active'] == False

    async def test_delete_not_authorized_user(self, ac, auth_ac):
            response = await ac.post("/users/delete/")

            assert response.status_code == 400
            assert response.json() == {"detail":"Токен отсутствует в заголовке"}