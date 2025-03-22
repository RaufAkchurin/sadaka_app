from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.google.schemas import GoogleUserAddDB
from app.client.google import get_user_info
from app.users.dao import UsersDAO
from app.users.schemas import UserBase, EmailModel


async def google_auth_service(code: str, session: AsyncSession) -> UserBase:
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
        authorized_user = await user_dao.add(values=update_data)
    else:
        await user_dao.update(filters=EmailModel(email=user_data.email), values=update_data)
        authorized_user = user

    return authorized_user
