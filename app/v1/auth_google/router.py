from fastapi import APIRouter, Depends, Response
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse, RedirectResponse

from app.exceptions import FailedGoogleOauthException
from app.settings import settings
from app.v1.auth.service_auth import set_tokens_to_response
from app.v1.auth_google.service import google_auth_service
from app.v1.dependencies.dao_dep import get_session_with_commit

v1_google_router = APIRouter()


@v1_google_router.get("/login/", response_class=RedirectResponse)
async def google_login():
    logger.error(f"Гугл авторизация \n {settings.google_redirect_to_service_url}")
    return JSONResponse(status_code=200, content={"redirect_url": settings.google_redirect_to_service_url})


@v1_google_router.get("/callback/")
async def google_auth(code: str, response: Response, session: AsyncSession = Depends(get_session_with_commit)):
    google_permitted_user = await google_auth_service(code, session)
    if google_permitted_user:
        set_tokens_to_response(response, google_permitted_user)
        return RedirectResponse(url=settings.GOOGLE_FINAL_REDIRECT_URI, headers=response.headers)
    else:
        raise FailedGoogleOauthException
