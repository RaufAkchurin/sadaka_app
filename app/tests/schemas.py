from httpx import AsyncClient, Cookies
from pydantic import BaseModel

class CookiesModel(BaseModel):
    user_access_token: str = None
    user_refresh_token: str = None

class AuthorizedClientModel(BaseModel):
    client: AsyncClient
    cookies: CookiesModel

    class Config:
        arbitrary_types_allowed = True