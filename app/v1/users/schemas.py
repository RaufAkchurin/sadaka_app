from typing import Self

from email_validator import EmailNotValidError, validate_email
from models.user import LanguageEnum
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class IdModel(BaseModel):
    id: int = Field(description="Электронная почта")
    model_config = ConfigDict(from_attributes=True)


class EmailModel(BaseModel):
    email: EmailStr = Field(description="Электронная почта")
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def check_email(self) -> Self:
        try:
            validate_email(str(self.email))
            return self
        except EmailNotValidError as e:
            raise ValueError(f"Невалидный email: {e}")


class UserBase(EmailModel):
    name: str = Field(min_length=3, max_length=50, description="Имя, от 3 до 50 символов")


class AnonymousUserAddDB(UserBase):
    is_anonymous: bool


class SUserEmailRegister(UserBase):
    password: str = Field(min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
    confirm_password: str = Field(min_length=5, max_length=50, description="Повторите пароль")

    @model_validator(mode="after")
    def check_password(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        return self


class SUserAddDB(UserBase):
    password: str = Field(min_length=5, description="Пароль в формате HASH-строки")
    is_active: bool = Field(description="Активный пользователь", default=True)


class SUserAuth(EmailModel):
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


class UserActiveModel(BaseModel):
    is_active: bool = Field(description="Активный пользователь")


class CityModel(BaseModel):
    id: int = Field(description="Идентификатор города")
    name: str = Field(description="Название города")

    model_config = ConfigDict(from_attributes=True)


class SUserInfo(UserBase):
    id: int = Field(description="Идентификатор пользователя")
    is_anonymous: bool = Field(description="Анонимный пользователь")
    is_active: bool = Field(description="Активный пользователь")
    city: CityModel = Field(description="Город пользователя")
    language: str = Field(description="Язык пользователя")
    picture_url: str | None = None
