from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.v1.auth_google.schemas import GoogleUserAddDBSchema
from app.v1.client.google_client import google_client
from app.v1.users.dao import UserDAO
from app.v1.users.schemas import UserContactsSchema


@dataclass
class GoogleAuthResult:
    """Wraps authenticated user with additional Google specific data."""

    user: User
    picture: str

    def __getattr__(self, item: str):
        # Forward attribute access to the underlying User instance.
        return getattr(self.user, item)


async def google_auth_service(code: str, session: AsyncSession) -> GoogleAuthResult:
    user_data = google_client.get_google_user_info(code)
    user_dao = UserDAO(session)
    user = await user_dao.find_one_or_none(filters=UserContactsSchema(email=user_data.email))
    update_data = GoogleUserAddDBSchema(
        name=user_data.name,
        email=user_data.email,
        google_access_token=user_data.google_access_token,
        is_active=True,
    )
    if not user:
        authorized_user = await user_dao.add(values=update_data)
    else:
        await user_dao.update(filters=UserContactsSchema(email=user_data.email), values=update_data)
        authorized_user = user

    return GoogleAuthResult(user=authorized_user, picture=str(user_data.picture))
