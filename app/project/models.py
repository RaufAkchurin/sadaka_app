import enum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.dao.database import Base
from app.geo.models import Region
from app.utils.validators import validate_link_url


class Project(Base):
    name: Mapped[str]
    description: Mapped[str | None]
    picture_url: Mapped[str | None]

    # region:
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), default=1, server_default=text("1"))
    region: Mapped["Region"] = relationship("Region", back_populates="regions", lazy="joined")

    # documents:
    # documents: Mapped[list["Document"]] = relationship(
    #     "Document",
    #     back_populates="project",
    #     cascade="all, delete-orphan"
    # )

    # # reports:
    # report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"))
    # report: Mapped["Report"] = relationship("Report", back_populates="reports", lazy="joined")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @validates("picture_url")
    def validate_link(self, key: str, value: str) -> str:
        return validate_link_url(value)


class StageStatusEnum(enum.Enum):
    ACTIVE = "active"
    FINISHED = "finished"


# class Stage(Base):
#     name: Mapped[str]
#     status: Mapped[StageStatusEnum] = mapped_column(
#         SqlEnum(StageStatusEnum, name="doc_type_enum"),
#         nullable=False,
#     )
#     goal: Mapped[int]
#
#     # reports:
#     report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"))
#     report: Mapped["Report"] = relationship("Report", back_populates="reports", lazy="joined")
