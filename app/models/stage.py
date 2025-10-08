from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.project import Project
from app.v1.dao.database import Base
from app.v1.project.enums import ProjectStatusEnum


class Stage(Base):
    __table_args__ = (UniqueConstraint("project_id", "number", name="unique_stage_number_per_project"),)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str]
    goal: Mapped[int]
    status: Mapped[ProjectStatusEnum] = mapped_column(
        SqlEnum(ProjectStatusEnum, name="stage_status_enum"),
        nullable=False,
    )

    # project:
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    project: Mapped["Project"] = relationship("Project", back_populates="stages", lazy="selectin")

    # file:
    reports: Mapped[list["File"]] = relationship(  # noqa: F821
        "File", back_populates="stage", cascade="all, delete-orphan", lazy="joined"
    )
    # payments:
    payments: Mapped[list["Payment"]] = relationship(  # noqa: F821
        "Payment", back_populates="stage", cascade="all, delete-orphan", lazy="joined"
    )

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.project_id}, name={self.status.value})"

    @validates("number")
    def validate_number(self, key, number):
        if not 1 <= number <= 5:
            raise ValueError("Stage number must be between 1 and 5.")
        return number

    @property
    def collected(self):
        collected: int = sum(payment.amount for payment in self.payments)
        return collected

    # TODO Add validation as active stage only one for project!
    # TODO Add validation if finished need report!!!
    # TODO calculated field who get % of progress
