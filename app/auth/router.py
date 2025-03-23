from fastapi import APIRouter, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.service_auth import authenticate_user, set_tokens
from app.dependencies.auth_dep import get_current_user, get_current_admin_user, check_refresh_token
from app.dependencies.dao_dep import get_session_with_commit, get_session_without_commit
from app.exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException
from app.users.dao import UsersDAO
from app.users.models import User
from app.users.schemas import SUserEmailRegister, SUserAuth, EmailModel, SUserAddDB, SUserInfo

router = APIRouter()


@router.post("/login/")
async def auth_user(
        response: Response,
        user_data: SUserAuth,
        session: AsyncSession = Depends(get_session_without_commit)
) -> dict:
    users_dao = UsersDAO(session)
    user = await users_dao.find_one_or_none(
        filters=EmailModel(email=user_data.email)
    )

    if not (user and await authenticate_user(user=user, password=user_data.password)):
        raise IncorrectEmailOrPasswordException
    set_tokens(response, user.id)
    return {
        'ok': True,
        'message': 'Авторизация успешна!'
    }



@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("user_access_token")
    response.delete_cookie("user_refresh_token")
    return {'message': 'Пользователь успешно вышел из системы'}


@router.post("/refresh")
async def process_refresh_token(
        response: Response,
        user: User = Depends(check_refresh_token)
):
    set_tokens(response, user.id)
    return {"message": "Токены успешно обновлены"}
