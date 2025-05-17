from pydantic import HttpUrl

from app.v1.users.schemas import UserBase


class GoogleUserData(UserBase):
    picture: HttpUrl
    google_access_token: str


class GoogleUserAddDB(UserBase):
    picture: str
    google_access_token: str
    is_active: bool
