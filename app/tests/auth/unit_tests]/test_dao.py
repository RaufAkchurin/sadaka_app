# import pytest
# from unittest.mock import MagicMock
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from pydantic import BaseModel
#
# from app.auth.dao import UsersDAO
# from app.dao.base import BaseDAO
#
#
# # Example Pydantic models for testing purposes
# class UserFilter(BaseModel):
#     id: int | None = None
#     email: str | None = None
#
#
# class UserCreate(BaseModel):
#     email: str
#     name: str
#
#
# # @pytest.fixture
# # async def session():
# #     # Mock session setup (usually, you would use a test database or mock the session)
# #     session = MagicMock(spec=AsyncSession)
# #     session.execute.return_value.scalar_one_or_none.return_value = None  # Default mock return
# #     yield session
# #     # Cleanup if needed
#
#
# @pytest.mark.parametrize("user_id, email, is_exist",
#                          [
#                              (1, "test1@test.com", True),
#                              (2, "test2@test.com", True),
#                              (99, ".............", False),
#                          ])
# async def test_find_one_or_none_by_id(session, user_id, email, is_exist):
#     # Mock the query result to simulate different test cases
#     if is_exist:
#         user = Users(id=user_id, email=email)
#         session.execute.return_value.scalar_one_or_none.return_value = user
#     else:
#         session.execute.return_value.scalar_one_or_none.return_value = None
#
#     dao = UsersDAO(session)
#     result = await dao.find_one_or_none_by_id(user_id)
#
#     if is_exist:
#         assert result
#         assert result.email == email
#     else:
#         assert result is None
#
#
# @pytest.mark.parametrize("filter_data, is_exist",
#                          [
#                              (UserFilter(id=1), True),
#                              (UserFilter(email="test2@test.com"), False),
#                              (UserFilter(), True),
#                          ])
# async def test_find_one_or_none(session, filter_data, is_exist):
#     # Mock the query result to simulate different test cases
#     if is_exist:
#         user = Users(id=1, email="test1@test.com")
#         session.execute.return_value.scalar_one_or_none.return_value = user
#     else:
#         session.execute.return_value.scalar_one_or_none.return_value = None
#
#     dao = UsersDAO(session)
#     result = await dao.find_one_or_none(filter_data)
#
#     if is_exist:
#         assert result
#         assert result.email == "test1@test.com"
#     else:
#         assert result is None
#
#
# @pytest.mark.parametrize("filters, expected_count",
#                          [
#                              (UserFilter(id=1), 1),
#                              (UserFilter(email="test2@test.com"), 0),
#                              (UserFilter(), 5),
#                          ])
# async def test_count(session, filters, expected_count):
#     # Mock the count result
#     session.execute.return_value.scalar.return_value = expected_count
#
#     dao = UsersDAO(session)
#     count = await dao.count(filters)
#
#     assert count == expected_count
#
#
# @pytest.mark.parametrize("user_data, expected_count",
#                          [
#                              (UserCreate(email="newuser@test.com", name="New User"), 1),
#                              (UserCreate(email="anotheruser@test.com", name="Another User"), 1),
#                          ])
# async def test_add(session, user_data, expected_count):
#     # Mock the return of the add method
#     new_user = Users(id=1, email=user_data.email, name=user_data.name)
#     session.flush.return_value = None  # Ensure the flush doesn't raise any errors
#     session.add.return_value = new_user
#
#     dao = UsersDAO(session)
#     added_user = await dao.add(user_data)
#
#     assert added_user
#     assert added_user.email == user_data.email
#     assert added_user.name == user_data.name
#
#
# @pytest.mark.parametrize("filter_data, update_data, rows_updated",
#                          [
#                              (UserFilter(id=1), UserCreate(email="updated@test.com", name="Updated User"), 1),
#                              (UserFilter(id=2), UserCreate(email="nonexistent@test.com", name="Nonexistent User"), 0),
#                          ])
# async def test_update(session, filter_data, update_data, rows_updated):
#     # Mock the result of the update query
#     session.execute.return_value.rowcount = rows_updated
#
#     dao = UsersDAO(session)
#     updated_rows = await dao.update(filter_data, update_data)
#
#     assert updated_rows == rows_updated
#
#
# @pytest.mark.parametrize("filter_data, rows_deleted",
#                          [
#                              (UserFilter(id=1), 1),
#                              (UserFilter(email="nonexistent@test.com"), 0),
#                          ])
# async def test_delete(session, filter_data, rows_deleted):
#     # Mock the result of the delete query
#     session.execute.return_value.rowcount = rows_deleted
#
#     dao = UsersDAO(session)
#     deleted_rows = await dao.delete(filter_data)
#
#     assert deleted_rows == rows_deleted
#
#
# @pytest.mark.parametrize("records, updated_count",
#                          [
#                              ([UserCreate(email="user1@test.com", name="User One")], 1),
#                              ([UserCreate(email="user2@test.com", name="User Two")], 1),
#                              ([UserCreate(email="nonexistent@test.com", name="Nonexistent User")], 0),
#                          ])
# async def test_bulk_update(session, records, updated_count):
#     # Mock the result of the bulk update query
#     session.execute.return_value.rowcount = updated_count
#
#     dao = UsersDAO(session)
#     updated_rows = await dao.bulk_update(records)
#
#     assert updated_rows == updated_count
from app.auth.dao import UsersDAO
from app.auth.schemas import SUserRegister, SUserAddDB


async def test_add_user_and_find_by_id(session):
    user_data_dict = {"email": "test99@test.com",
                     "phone_number": "+74444444499",
                     "first_name": "test4",
                     "last_name": "test4",
                     "password": "8654567"}

    user_dao = UsersDAO(session)
    new_user = await user_dao.add(values=SUserAddDB(**user_data_dict))
    assert new_user.id == 6

    user = await user_dao.find_one_or_none_by_id(new_user.id)
    assert user.email == "test99@test.com"



#TODO add roles

