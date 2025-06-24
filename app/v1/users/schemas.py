from typing import Self

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models.user import LanguageEnum


class IdSchema(BaseModel):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserEmailSchema(BaseModel):
    email: EmailStr = Field(description="Электронная почта")
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def check_email(self) -> Self:
        try:
            validate_email(str(self.email))
            return self
        except EmailNotValidError as e:
            raise ValueError(f"Невалидный email: {e}")


class UserBaseSchema(UserEmailSchema):
    name: str = Field(min_length=3, max_length=50, description="Имя, от 3 до 50 символов")


class AnonymousUserAddSchemaSchema(UserBaseSchema):
    is_anonymous: bool


class SUserEmailRegisterSchemaSchema(UserBaseSchema):
    password: str = Field(min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
    confirm_password: str = Field(min_length=5, max_length=50, description="Повторите пароль")

    @model_validator(mode="after")
    def check_password(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        return self


class SUserAddSchemaSchema(UserBaseSchema):
    password: str = Field(min_length=5, description="Пароль в формате HASH-строки")
    is_active: bool = Field(description="Активный пользователь", default=True)


class SUserAuthSchema(UserEmailSchema):
    password: str = Field(min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")


class UserDataUpdateSchema(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="Имя, от 3 до 50 символов",
    )
    email: EmailStr | None = Field(default=None, description="Электронная почта")
    city_id: int | None = Field(default=None, description="Идентификатор города", gt=0)
    language: LanguageEnum | None = Field(default=None)

    class Config:
        use_enum_values = True


class PictureIdSchema(BaseModel):
    picture_id: int = Field(description="Картинка пользователя")


class UserActiveSchema(BaseModel):
    is_active: bool = Field(description="Активный пользователь")


class CitySchema(BaseModel):
    id: int = Field(description="Идентификатор города")
    name: str = Field(description="Название города")

    model_config = ConfigDict(from_attributes=True)


class SUserInfoSchemaSchema(UserBaseSchema):
    id: int = Field(description="Идентификатор пользователя")
    is_anonymous: bool = Field(description="Анонимный пользователь")
    is_active: bool = Field(description="Активный пользователь")
    city: CitySchema = Field(description="Город пользователя")
    language: str = Field(description="Язык пользователя")
    picture_url: str | None = None
