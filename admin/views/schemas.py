import enum

from pydantic import BaseModel
from v1.users.enums import RoleEnum


class TokenTypeEnum(str, enum.Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenPayloadSchema(BaseModel):
    # payload
    user_id: int
    user_role: RoleEnum
    funds_access_ids: list[int]

    # core data
    exp: int
    type: TokenTypeEnum
