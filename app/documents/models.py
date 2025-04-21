from dataclasses import dataclass
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.dao.database import Base
from app.utils.validators import validate_link_url


@dataclass
class Document(Base):
    name: Mapped[str]
    size: Mapped[int]
    url: Mapped[str]

    fund_id: Mapped[int | None] = mapped_column(ForeignKey("funds.id"), nullable=True)
    fund: Mapped["Fund"] = relationship("Fund", back_populates="documents")

    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    project: Mapped["Project"] = relationship("Project", back_populates="documents")

    stage_id: Mapped[int | None] = mapped_column(ForeignKey("stages.id"), nullable=True)
    stage: Mapped["Stage"] = relationship("Stage", back_populates="reports")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @validates("fund_id", "project_id", "stage_id")
    def validate_single_target(self, key, value):
        fund_id = value if key == "fund_id" else self.fund_id
        project_id = value if key == "project_id" else self.project_id
        stage_id = value if key == "stage_id" else self.stage_id

        ids = [fund_id, project_id, stage_id]
        num_set = sum(bool(i) for i in ids)

        if num_set == 0:
            raise ValueError("Document must be related to at least one model (project or fund).")
        if num_set > 1:
            raise ValueError("Document must be related to only one model (project or fund) not multiple.")

        return value

    @validates("url")
    def validate_link(self, key: str, value: str) -> str:
        return validate_link_url(value)
