from dataclasses import dataclass
from typing import Optional
from sqlalchemy import text, ForeignKey, Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.dao.database import Base, str_uniq, DATABASE_URL

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
    anonymous: Mapped[bool] = False

    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), default=1, server_default=text("1"))
    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="joined")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
