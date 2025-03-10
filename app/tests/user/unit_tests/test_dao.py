import pytest

from app.auth.dao import UsersDAO, RoleDAO


@pytest.mark.parametrize("user_id, email, is_exist",
[
                         (1, "test1@test.com", True),
                         (2, "test2@test.com", True),
                         (99, ".............", False),
])
async def test_find_one_or_none_by_id(session, user_id, email, is_exist):
    user = await UsersDAO(session).find_one_or_none_by_id(data_id=user_id)
    if is_exist:
        assert user
        assert user.email == email
    else:
        assert user is None

