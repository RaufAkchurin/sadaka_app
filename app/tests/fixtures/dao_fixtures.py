import pytest

from app.v1.users.dao import CommentDAO, OneTimePassDAO, UserDAO


@pytest.fixture(scope="function")
async def user_dao(session) -> UserDAO:
    user_dao = UserDAO(session)
    return user_dao


@pytest.fixture(scope="function")
async def otp_dao(session) -> OneTimePassDAO:
    otp_dao = OneTimePassDAO(session)
    return otp_dao


@pytest.fixture(scope="function")
async def comment_dao(session) -> CommentDAO:
    comment_dao = CommentDAO(session)
    return comment_dao
