from datetime import datetime
from typing import Optional, Self

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models.user import LanguageEnum
from app.v1.api_utils.validators import validate_phone


class IdSchema(BaseModel):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserContactsSchema(BaseModel):
    email: Optional[EmailStr] = Field(default=None, description="Электронная почта")
    phone: Optional[str] = Field(
        default=None, min_length=12, max_length=12, description="Телефон, в формате +7xxxxxxxxxx"
    )
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def check_contacts(self) -> Self:
        # Проверка на обязательность хотя бы одного поля
        if not self.email and not self.phone:
            raise ValueError("Обязательно одно из двух поля: EMAIL или PHONE")

        # Если email отсутствует, телефон обязателен
        if not self.phone and self.email is None:
            raise ValueError("Телефон обязателен, если email не передан.")

        # Если оба поля присутствуют, можно делать дополнительные проверки
        if self.email:
            try:
                validate_email(str(self.email))
            except EmailNotValidError as e:
                raise ValueError(f"Невалидный email: {e}")

        if self.phone:
            validate_phone(str(self.phone))

        return self


class UserPhoneOnlySchema(BaseModel):
    phone: str = Field(min_length=12, max_length=12, description="Телефон, в формате +7xxxxxxxxxx")
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def check_contacts(self) -> Self:
        if self.phone:
            validate_phone(str(self.phone))

        return self


class UserCodeCheckSchema(UserPhoneOnlySchema):
    confirmation_code: str = Field(min_length=6, max_length=6, description="Код подтверждения в формате 123456")


class UserCodeAddSchema(UserPhoneOnlySchema):
    confirmation_code: int = Field(description="Код подтверждения")
    confirmation_code_expiry: datetime = Field()
    is_active: bool = Field(description="Активный пользователь", default=False)

    model_config = ConfigDict(from_attributes=True)


class UserBaseSchema(UserContactsSchema):
    name: str | None = Field(min_length=3, max_length=50, description="Имя, от 3 до 50 символов")


class AnonymousUserAddSchema(UserBaseSchema):
    is_anonymous: bool


class SUserEmailRegisterSchema(UserBaseSchema):
    password: str = Field(min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
    confirm_password: str = Field(min_length=5, max_length=50, description="Повторите пароль")

    @model_validator(mode="after")
    def check_password(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        return self


class SUserAddSchema(UserBaseSchema):
    password: str = Field(min_length=5, description="Пароль в формате HASH-строки")
    is_active: bool = Field(description="Активный пользователь", default=True)


class SUserAuthPasswordSchema(UserContactsSchema):
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


class SUserInfoSchema(UserBaseSchema):
    id: int = Field(description="Идентификатор пользователя")
    is_anonymous: bool = Field(description="Анонимный пользователь")
    is_active: bool = Field(description="Активный пользователь")
    city: CitySchema = Field(description="Город пользователя")
    language: str = Field(description="Язык пользователя")
    picture_url: str | None = None
