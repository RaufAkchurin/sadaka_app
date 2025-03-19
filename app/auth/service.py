from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dao import UsersDAO
from app.auth.schemas import EmailModel
from app.auth.schemas_auth import GoogleUserAddDB
from app.auth.service_jwt import verify_password
from app.client.google import get_user_info
from app.settings import settings

async def google_auth_service(code: str, session: AsyncSession) -> None:
    user_data = get_user_info(code)
    user_dao = UsersDAO(session)
    user = await user_dao.find_one_or_none(filters=EmailModel(email=user_data.email))
    update_data = GoogleUserAddDB(
        name=user_data.name,
        email=user_data.email,
        google_access_token=user_data.google_access_token,
        picture=str(user_data.picture)
    )

    if not user:
        await user_dao.add(values=update_data)
    else:
        await user_dao.update(filters=EmailModel(email=user_data.email), values=update_data)


def create_tokens(data: dict) -> dict:
    # Текущее время в UTC
    now = datetime.now(timezone.utc)

    # AccessToken - 30 минут
    access_expire = now + timedelta(seconds=10)
    access_payload = data.copy()
    access_payload.update({"exp": int(access_expire.timestamp()), "type": "access"})
    access_token = jwt.encode(
        access_payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    # RefreshToken - 7 дней
    refresh_expire = now + timedelta(days=7)
    refresh_payload = data.copy()
    refresh_payload.update({"exp": int(refresh_expire.timestamp()), "type": "refresh"})
    refresh_token = jwt.encode(
        refresh_payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


async def authenticate_user(user, password):
    if not user or verify_password(plain_password=password, hashed_password=user.password) is False:
        return None
    return user


def set_tokens(response: Response, user_id: int):
    new_tokens = create_tokens(data={"sub": str(user_id)})
    access_token = new_tokens.get('access_token')
    refresh_token = new_tokens.get("refresh_token")

    response.set_cookie(
        key="user_access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax"
    )

    response.set_cookie(
        key="user_refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax"
    )