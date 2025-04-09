from typing import Optional
from dataclasses import dataclass
from sqlalchemy import text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.dao.database import Base, str_uniq
from app.geo.models import City
import enum
from sqlalchemy import Enum as SqlEnum

class LanguageEnum(enum.Enum):
    RU = "RU"
    EN = "EN"

@dataclass
class Role(Base):
    name: Mapped[str_uniq]
    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"


@dataclass
class User(Base):
    name: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[Optional[str]]
    picture: Mapped[Optional[str]]

    google_access_token: Mapped[Optional[str]]
    language: Mapped[LanguageEnum] = mapped_column(
        SqlEnum(LanguageEnum, name="language_enum"),
        server_default=LanguageEnum.RU.value,
        default=LanguageEnum.RU.value,
        nullable=False
    )
    is_anonymous: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Связь с городом
    city_id: Mapped[int] = mapped_column(ForeignKey('citys.id'), default=1, server_default=text("1"))
    city: Mapped["City"] = relationship("City", back_populates="users", lazy="joined")

    # Связь с ролью
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), default=1, server_default=text("1"))
    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="joined")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

