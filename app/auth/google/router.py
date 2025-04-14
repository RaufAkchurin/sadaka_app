from fastapi import APIRouter, Depends, Response
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from app.auth.google.service import google_auth_service
from app.auth.service_auth import set_tokens
from app.client.google_client import google_client
from app.dependencies.dao_dep import get_session_with_commit
from app.exceptions import FailedGoogleOauthException

google_router = APIRouter()


@google_router.get("/login/", response_class=RedirectResponse)
async def google_login():
    redirect_url = google_client.google_redirect_url
    logger.error(f"Гугл авторизация \n {redirect_url}")
    return RedirectResponse(redirect_url)


@google_router.get("/callback/")
async def google_auth(
    code: str,
    response: Response,
    session: AsyncSession = Depends(get_session_with_commit),
):
    google_permitted_user = await google_auth_service(code, session)
    if google_permitted_user:
        set_tokens(response, google_permitted_user.id)
        return RedirectResponse(url="http://localhost:8000/users/me", headers=response.headers)
    else:
        raise FailedGoogleOauthException
