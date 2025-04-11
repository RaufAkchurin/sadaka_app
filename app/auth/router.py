from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service_auth import authenticate_user, set_tokens
from app.dependencies.auth_dep import check_refresh_token
from app.dependencies.dao_dep import get_session_with_commit, get_session_without_commit
from app.exceptions import IncorrectEmailOrPasswordException
from app.tests.factory.mimesis import person
from app.users.dao import UsersDAO
from app.users.models import User
from app.users.schemas import (
    AnonymousUserAddDB,
    EmailModel,
    SUserAddDB,
    SUserAuth,
    SUserEmailRegister,
    UserActiveModel,
    UserDataUpdateSchema,
)

auth_router = APIRouter()


@auth_router.post("/register/")
async def register_by_email(
    user_data: SUserEmailRegister,
    session: AsyncSession = Depends(get_session_with_commit),
) -> dict:
    user_dao = UsersDAO(session)
    existing_user = await user_dao.find_one_or_none(
        filters=EmailModel(email=user_data.email)
    )
    if existing_user:
        await UsersDAO(session).update(
            filters=EmailModel(email=existing_user.email),
            values=UserActiveModel(is_active=True),
        )
    else:
        user_data_dict = user_data.model_dump()
        user_data_dict.pop("confirm_password", None)

        await user_dao.add(values=SUserAddDB(**user_data_dict, is_active=True))
    return {"message": "Вы успешно зарегистрированы!"}


@auth_router.post("/login_anonymous/")
async def register_and_login_anonymous(
    response: Response, session: AsyncSession = Depends(get_session_with_commit)
) -> dict:
    user_dao = UsersDAO(session)
    user = await user_dao.add(
        values=AnonymousUserAddDB(
            email=person.email(), name=person.name(), is_anonymous=True
        )
    )
    set_tokens(response, user.id)
    return {"message": "Анонимный пользователь добавлен"}


@auth_router.post("/login/")
async def login_by_email(
    response: Response,
    user_data: SUserAuth,
    session: AsyncSession = Depends(get_session_without_commit),
) -> dict:
    users_dao = UsersDAO(session)
    user = await users_dao.find_one_or_none(filters=EmailModel(email=user_data.email))

    if not (user and await authenticate_user(user=user, password=user_data.password)):
        raise IncorrectEmailOrPasswordException
    set_tokens(response, user.id)
    return {"ok": True, "message": "Авторизация успешна!"}


@auth_router.get("/logout")
async def logout(response: Response):
    response.delete_cookie("user_access_token")
    response.delete_cookie("user_refresh_token")
    return {"message": "Пользователь успешно вышел из системы"}


@auth_router.post("/refresh")
async def process_refresh_token(
    response: Response, user: User = Depends(check_refresh_token)
):
    set_tokens(response, user.id)
    return {"message": "Токены успешно обновлены"}
