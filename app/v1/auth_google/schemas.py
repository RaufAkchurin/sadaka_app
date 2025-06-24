from pydantic import BaseModel, HttpUrl

from app.v1.users.schemas import UserBaseSchema


class GoogleUserDataSchema(UserBaseSchema):
    picture: HttpUrl
    google_access_token: str


class GoogleUserAddDBSchema(UserBaseSchema):
    # picture: str  # if you need picture you can create file instance with photo then add it to user profile
    google_access_token: str
    is_active: bool


class GoogleRedirectUrl(BaseModel):
    redirect_url: str
