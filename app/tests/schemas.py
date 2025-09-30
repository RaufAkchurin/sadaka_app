import datetime
import uuid

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


class TestPaymentAddSchema(BaseModel):
    id: uuid.UUID
    user_id: int
    project_id: int
    stage_id: int
    referral_id: int | None = None
    amount: float | None = None
    income_amount: float = 0.0
    created_at: datetime.datetime | None = datetime.datetime.now()  # передавать значения всеравно приходится(
    updated_at: datetime.datetime | None = datetime.datetime.now()
    captured_at: datetime.datetime | None = datetime.datetime.now()


class CookiesModel(BaseModel):
    user_access_token: str = None
    user_refresh_token: str = None


class AuthorizedClientModel(BaseModel):
    client: AsyncClient
    cookies: CookiesModel

    class Config:
        arbitrary_types_allowed = True  # чтобы AsyncClient был принят в pydantic модели
