from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import IncorrectEmailOrPasswordException
from app.models.user import User
from app.tests.factory.mimesis import person
from app.v1.auth.service_auth import authenticate_user, set_tokens_to_response
from app.v1.dependencies.auth_dep import check_refresh_token
from app.v1.dependencies.dao_dep import get_session_with_commit, get_session_without_commit
from app.v1.users.dao import UserDAO
from app.v1.users.schemas import (
    AnonymousUserAddSchema,
    SUserAddSchema,
    SUserAuthPasswordSchema,
    SUserEmailRegisterSchema,
    UserActiveSchema,
    UserContactsSchema,
)

v1_auth_router = APIRouter(tags=["Auth v1"])
v2_auth_router = APIRouter(tags=["Auth v2"])


@v1_auth_router.post("/register/")
async def register_by_email(
    user_data: SUserEmailRegisterSchema,
    session: AsyncSession = Depends(get_session_with_commit),
) -> dict:
    user_dao = UserDAO(session)
    existing_user = await user_dao.find_one_or_none(filters=UserContactsSchema(email=user_data.email))
    if existing_user:
        await UserDAO(session).update(
            filters=UserContactsSchema(email=existing_user.email),
            values=UserActiveSchema(is_active=True),
        )
    else:
        user_data_dict = user_data.model_dump()
        user_data_dict.pop("confirm_password", None)

        await user_dao.add(values=SUserAddSchema(**user_data_dict, is_active=True))
    return {"message": "Вы успешно зарегистрированы!"}


@v1_auth_router.post("/login_anonymous/")
async def register_and_login_anonymous(
    response: Response, session: AsyncSession = Depends(get_session_with_commit)
) -> dict:
    user_dao = UserDAO(session)
    user = await user_dao.add(
        values=AnonymousUserAddSchema(
            email=person.email(domains=["first.com", "second.ru"]), name=person.name(), is_anonymous=True
        )
    )
    set_tokens_to_response(response, user)
    return {"message": "Анонимный пользователь добавлен"}


@v1_auth_router.post("/login/")
async def login_by_email(
    response: Response,
    user_data: SUserAuthPasswordSchema,
    session: AsyncSession = Depends(get_session_without_commit),
) -> dict:
    users_dao = UserDAO(session)
    user = await users_dao.find_one_or_none(filters=UserContactsSchema(email=user_data.email))

    if not (user and await authenticate_user(user=user, password=user_data.password)):
        raise IncorrectEmailOrPasswordException
    set_tokens_to_response(response, user)
    return {"ok": True, "message": "Авторизация успешна!"}


@v1_auth_router.get("/logout")
async def logout(response: Response):
    response.delete_cookie("user_access_token")
    response.delete_cookie("user_refresh_token")
    return {"message": "Пользователь успешно вышел из системы"}


@v1_auth_router.post("/refresh")
async def process_refresh_token(response: Response, user: User = Depends(check_refresh_token)):
    set_tokens_to_response(response, user)
    return {"message": "Токены успешно обновлены"}


# NOT USED IN PROD! BUT DON'T DELETE IT!
@v2_auth_router.post("/versioning_for_example")
async def versioning_for_example(response: Response, user: User = Depends(check_refresh_token)):
    set_tokens_to_response(response, user)
    return {"message": "Токены успешно обновлены"}


@v2_auth_router.get("/sentry-debug")
async def trigger_error():
    1 / 0
