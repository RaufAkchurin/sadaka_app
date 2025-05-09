from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.dao.database import Base
from app.fund.models import Fund
from app.project.enums import AbstractStatusEnum


class Project(Base):
    name: Mapped[str]
    status: Mapped[AbstractStatusEnum] = mapped_column(
        SqlEnum(AbstractStatusEnum, name="project_status_enum"),
        nullable=False,
    )
    description: Mapped[str | None]
    goal: Mapped[int]

    fund_id: Mapped[int] = mapped_column(ForeignKey("funds.id"), nullable=False)
    fund: Mapped["Fund"] = relationship("Fund", back_populates="projects", lazy="joined")

    documents: Mapped[list["File"]] = relationship(  # noqa: F821
        "File",
        back_populates="project_document",
        cascade="all, delete-orphan",
        foreign_keys="[File.project_document_id]",
        lazy="joined",
    )

    pictures: Mapped[list["File"]] = relationship(  # noqa: F821
        "File",
        back_populates="project_picture",
        cascade="all, delete-orphan",
        foreign_keys="[File.project_picture_id]",
        lazy="joined",
    )

    stages: Mapped[list["Stage"]] = relationship(  # noqa: F821
        "Stage", back_populates="project", cascade="all, delete-orphan", lazy="joined"
    )

    payments: Mapped[list["Payment"]] = relationship(  # noqa: F821
        "Payment", back_populates="project", cascade="all, delete-orphan", lazy="joined"
    )

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @validates("documents")
    def validate_documents_count(self, key, document):
        if len(self.documents) >= 5:
            raise ValueError("You can't have more than 5 documents.")
        return document


class Stage(Base):
    __table_args__ = (UniqueConstraint("project_id", "number", name="unique_stage_number_per_project"),)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str]
    goal: Mapped[int]
    status: Mapped[AbstractStatusEnum] = mapped_column(
        SqlEnum(AbstractStatusEnum, name="stage_status_enum"),
        nullable=False,
    )

    # project:
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    project: Mapped["Project"] = relationship("Project", back_populates="stages", lazy="joined")

    # file:
    reports: Mapped[list["File"]] = relationship(  # noqa: F821
        "File", back_populates="stage", cascade="all, delete-orphan"
    )
    # payments:
    payments: Mapped[list["Payment"]] = relationship(  # noqa: F821
        "Payment", back_populates="stage", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.project_id}, name={self.status.value})"

    @validates("number")
    def validate_number(self, key, number):
        if not 1 <= number <= 5:
            raise ValueError("Stage number must be between 1 and 5.")
        return number

    # TODO Add validation as active stage only one for project!
    # TODO Add validation if finished need report!!!
    # TODO calculated field who get % of progress
