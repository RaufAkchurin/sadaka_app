from dataclasses import dataclass

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.dao.database import Base
from app.utils.validators import validate_phone


@dataclass
class Fund(Base):
    # core:
    name: Mapped[str]
    description: Mapped[str | None]

    # contacts:
    hot_line: Mapped[str]
    address: Mapped[str]

    # region:
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), default=1, server_default=text("1"))
    region: Mapped["Region"] = relationship(  # noqa F821
        "Region", back_populates="funds", lazy="joined"
    )  # imported in __init__.py

    picture_id: Mapped[int | None] = mapped_column(ForeignKey("files.id"), nullable=True, unique=True)
    picture: Mapped["File | None"] = relationship(  # noqa F821
        "File",  # noqa F821
        back_populates="fund_picture",
        foreign_keys=[picture_id],
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="joined",
    )

    # file:
    documents: Mapped[list["File"]] = relationship(  # noqa F821
        "File",
        back_populates="fund_document",
        cascade="all, delete-orphan",
        foreign_keys="[File.fund_document_id]",
    )

    # projects:
    projects: Mapped[list["Project"]] = relationship(  # noqa F821
        "Project", back_populates="fund", cascade="all, delete-orphan"
    )  # imported in __init__.py

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @validates("hot_line")
    def validate_hot_line(self, key: str, value: str):
        return validate_phone(value)
