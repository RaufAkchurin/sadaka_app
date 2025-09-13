from pydantic import BaseModel, ConfigDict, Field

from app.v1.project.enums import AbstractStatusEnum


class UserModelTotalIncomeSchema(BaseModel):
    id: int
    name: str | None = None
    url: str | None = Field(default=None, alias="picture_url")
    total_income: float = 0

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RegionModelTotalIncomeSchema(BaseModel):
    id: int
    name: str
    url: str | None = Field(default=None, alias="picture_url")
    total_income: float = 0

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProjectRatingSchema(BaseModel):
    id: int
    name: str
    status: AbstractStatusEnum
    fund_name: str
    picture_url: str | None = None
    total_income: float = 0
    unique_sponsors: int
    count_comments: int

    model_config = ConfigDict(from_attributes=True)


class RatingTotalInfoResponseSchema(BaseModel):
    payments: int = 0
    autopayments: int = 0
    cities: int = 0
    projects: int = 0
    total_income: float = 0
