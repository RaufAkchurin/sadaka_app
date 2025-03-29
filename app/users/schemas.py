from typing import Self, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator, computed_field, HttpUrl

from app.auth.service_jwt import get_password_hash


class EmailModel(BaseModel):
    email: EmailStr = Field(description="Электронная почта")
    model_config = ConfigDict(from_attributes=True)


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
        self.password = get_password_hash(self.password)  # хешируем пароль до сохранения в базе данных
        return self


class SUserAddDB(UserBase):
    password: str = Field(min_length=5, description="Пароль в формате HASH-строки")


class SUserAuth(EmailModel):
    password: str = Field(min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")


class RoleModel(BaseModel):
    id: int = Field(description="Идентификатор роли")
    name: str = Field(description="Название роли")
    model_config = ConfigDict(from_attributes=True)


class UserUpdateAPI(UserBase):
    picture: str = Field(description="Аватарка")
    city_id: int = Field(description="Идентификатор города")

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
    picture: Optional[str]
    city: CityModel = Field(exclude=True)
    role: RoleModel = Field(exclude=True)

    @computed_field
    def role_name(self) -> str:
        return self.role.name

    @computed_field
    def role_id(self) -> int:
        return self.role.id

    @computed_field
    def city_name(self) -> str:
        return self.city.name

    @computed_field
    def city_id(self) -> int:
        return self.city.id



