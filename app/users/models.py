from dataclasses import dataclass

from email_validator import EmailNotValidError, validate_email
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.dao.database import Base, str_uniq
from app.geo.models import City
from app.users.enums import LanguageEnum
from app.utils.validators import validate_link_url


@dataclass
class Role(Base):
    name: Mapped[str_uniq]
    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"


@dataclass
class User(Base):
    name: Mapped[str]
    password: Mapped[str | None]
    picture_url: Mapped[str | None]

    google_access_token: Mapped[str | None]
    language: Mapped[LanguageEnum] = mapped_column(
        SqlEnum(LanguageEnum, name="language_enum"),
        server_default=LanguageEnum.RU.value,
        default=LanguageEnum.RU.value,
        nullable=False,
    )
    is_anonymous: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    email: Mapped[str] = mapped_column(unique=True, nullable=False)

    # Связь с городом
    city_id: Mapped[int] = mapped_column(ForeignKey("citys.id"), default=1, server_default=text("1"))
    city: Mapped["City"] = relationship("City", back_populates="users", lazy="joined")

    # Связь с ролью
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=1, server_default=text("1"))
    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="joined")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @validates("picture_url")
    def validate_link(self, key: str, value: str) -> str:
        return validate_link_url(value)

    @validates("email")
    def validate_email_field(self, key, value):
        try:
            valid = validate_email(value)
            return valid.normalized
        except EmailNotValidError as e:
            raise ValueError(f"Невалидный email: {e}")
