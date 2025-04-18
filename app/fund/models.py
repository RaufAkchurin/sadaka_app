from dataclasses import dataclass

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.dao.database import Base
from app.documents.models import Document
from app.utils.validators import validate_link_url


@dataclass
class Fund(Base):
    name: Mapped[str]
    description: Mapped[str | None]
    picture_url: Mapped[str]

    # region:
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), default=1, server_default=text("1"))
    region: Mapped["Region"] = relationship("Region", back_populates="funds", lazy="joined")  # imported in __init__.py

    # documents:
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="fund", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @validates("picture_url")
    def validate_link(self, key: str, value: str) -> str:
        return validate_link_url(value)
