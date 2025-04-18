from dataclasses import dataclass

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.dao.database import Base
from app.utils.validators import validate_link_url, validate_phone


@dataclass
class Fund(Base):
    # core:
    name: Mapped[str]
    description: Mapped[str | None]
    picture_url: Mapped[str]

    # contacts:
    hot_line: Mapped[str]
    address: Mapped[str]

    # region:
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), default=1, server_default=text("1"))
    region: Mapped["Region"] = relationship("Region", back_populates="funds", lazy="joined")  # imported in __init__.py

    # documents:
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="fund", cascade="all, delete-orphan")
    # projects:
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="funds", cascade="all, delete-orphan"
    )  # imported in __init__.py

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @validates("picture_url")
    def validate_link(self, key: str, value: str) -> str:
        return validate_link_url(value)

    @validates("hot_line")
    def validate_hot_line(self, key: str, value: str):
        return validate_phone(value)
