from pydantic import BaseModel, EmailStr, HttpUrl

from app.auth.schemas import UserBase


class GoogleUserData(UserBase):
    picture: HttpUrl
    google_access_token : str


class GoogleUserAddDB(UserBase):
    picture: str
    google_access_token : str