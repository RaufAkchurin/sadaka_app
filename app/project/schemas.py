from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.project.enums import AbstractStatusEnum


class FileSchema(BaseModel):
    id: int
    name: str
    url: str
    type: str
    mime: str

    model_config = ConfigDict(from_attributes=True)


class FundShortSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class StageSchema(BaseModel):
    id: int
    name: str
    description: str
    goal: int
    status: AbstractStatusEnum

    model_config = ConfigDict(from_attributes=True)


class ProjectInfoSchema(BaseModel):
    id: int
    name: str
    status: AbstractStatusEnum
    description: Optional[str]

    # funds: List[FundShortSchema] = []
    documents: List[FileSchema] = []
    pictures: List[FileSchema] = []
    stages: List[StageSchema] = []

    model_config = ConfigDict(from_attributes=True)
