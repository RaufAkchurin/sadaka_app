from dns.message import make_response
from fastapi import Response, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse, JSONResponse
from app.auth.service_auth import set_tokens, google_auth_service
from app.client.google import get_google_redirect_url
from app.dependencies.dao_dep import get_session_with_commit

from fastapi import APIRouter

router = APIRouter()


@router.get('/login/', response_class=RedirectResponse)
async def google_login():
    redirect_url = get_google_redirect_url()
    logger.error(f"Перейдите по ссылке для Гугл авторизации {redirect_url}")
    return RedirectResponse(redirect_url)

@router.get('/callback/')
async def google_auth(code: str,
                    response: Response,
                    session: AsyncSession = Depends(get_session_with_commit),
                      ):
    google_authorized_user = await google_auth_service(code, session)
    if google_authorized_user:
        # Создаем ответ и устанавливаем куку с токеном
        # Шаг 4: Устанавливаем JWT токен в куку
        response = JSONResponse(content={"message": "Success"})
        set_tokens(response, google_authorized_user.id)
        # Шаг 5: Редиректим пользователя на нужную страницу
        return RedirectResponse(url="http://localhost:8000/docs#/Auth/get_me_auth_me__get", headers=response.headers)