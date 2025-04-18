from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.dao.database import Base
from app.fund.models import Fund
from app.project.enums import StageStatusEnum
from app.utils.validators import validate_link_url


class Project(Base):
    name: Mapped[str]
    description: Mapped[str | None]
    picture_url: Mapped[str | None]

    fund_id: Mapped[int] = mapped_column(ForeignKey("funds.id"), nullable=False)
    funds: Mapped["Fund"] = relationship("Fund", back_populates="projects", lazy="joined")

    # documents:
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @validates("picture_url")
    def validate_link(self, key: str, value: str) -> str:
        return validate_link_url(value)


class Stage(Base):
    name: Mapped[str]
    status: Mapped[StageStatusEnum] = mapped_column(
        SqlEnum(StageStatusEnum, name="stage_status_enum"),
        nullable=False,
    )
    goal: Mapped[int]

    # documents:
    reports: Mapped[list["Document"]] = relationship("Document", back_populates="stage", cascade="all, delete-orphan")
