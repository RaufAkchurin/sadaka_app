from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class CommentSchema(BaseModel):
    user_id: int
    project_id: int
    content: str

    model_config = ConfigDict(from_attributes=True)


class CommentCreateDataSchema(BaseModel):
    project_id: int = Field(ge=1)
    content: str = Field(min_length=1, max_length=250)

    model_config = ConfigDict(from_attributes=True)


class CommentContentSchema(BaseModel):
    content: str = Field(min_length=1, max_length=250)

    model_config = ConfigDict(from_attributes=True)


class CommentInfoSchema(BaseModel):
    id: int
    user_id: int
    project_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentProjectFilterSchema(BaseModel):
    project_id: int

    model_config = ConfigDict(from_attributes=True)


class CommentsInfoSchema(BaseModel):
    comments: List[CommentInfoSchema]
