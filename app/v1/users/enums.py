import enum


class LanguageEnum(str, enum.Enum):
    RU = "RU"
    EN = "EN"


class RoleEnum(str, enum.Enum):
    SUPERUSER = "superuser"
    FUND_ADMIN = "fund_admin"
    FUND_STAFF = "fund_staff"
    USER = "user"
