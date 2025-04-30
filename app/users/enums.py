import enum


class LanguageEnum(enum.Enum):
    RU = "RU"
    EN = "EN"


class RoleEnum(enum.Enum):
    SUPERUSER = "superuser"
    FUND_ADMIN = "fund_admin"
    USER = "user"
