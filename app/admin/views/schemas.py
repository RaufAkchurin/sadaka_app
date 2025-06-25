import enum

from pydantic import BaseModel


class RoleEnum(str, enum.Enum):
    SUPERUSER = "superuser"
    FUND_ADMIN = "fund_admin"
    FUND_STAFF = "fund_staff"
    USER = "user"


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
