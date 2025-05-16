from pydantic import HttpUrl

from app.users.v1.schemas import UserBase


class GoogleUserData(UserBase):
    picture: HttpUrl
    google_access_token: str


class GoogleUserAddDB(UserBase):
    picture: str
    google_access_token: str
    is_active: bool
