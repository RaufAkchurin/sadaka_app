from dataclasses import dataclass

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dao.database import Base


@dataclass
class Payment(Base):
    amount: Mapped[int]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="payments", lazy="joined")  # noqa: F821

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    project: Mapped["Project"] = relationship("Project", back_populates="payments", lazy="joined")  # noqa: F821

    stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"), nullable=False)
    stage: Mapped["Stage"] = relationship("Stage", back_populates="payments", lazy="joined")  # noqa: F821

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, project={self.project_id}, amount={self.amount})"
