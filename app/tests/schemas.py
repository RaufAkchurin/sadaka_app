from httpx import AsyncClient
from pydantic import BaseModel


class TestRegionAddSchema(BaseModel):
    id: int
    name: str
    country_id: int


class TestCityAddSchema(BaseModel):
    id: int
    name: str
    region_id: int


class TestUserAddSchema(BaseModel):
    id: int
    name: str
    email: str
    password: str
    city_id: int


class CookiesModel(BaseModel):
    user_access_token: str = None
    user_refresh_token: str = None


class AuthorizedClientModel(BaseModel):
    client: AsyncClient
    cookies: CookiesModel

    class Config:
        arbitrary_types_allowed = True  # чтобы AsyncClient был принят в pydantic модели
