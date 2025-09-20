from dataclasses import dataclass

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.v1.dao.database import Base


@dataclass
class Comment(Base):
    content: Mapped[str]

    # Project relations
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = relationship("User", back_populates="comments", lazy="noload")  # noqa F821

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    project: Mapped["Project"] = relationship("Project", back_populates="comments", lazy="noload")  # noqa F821

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, project={self.project.name})"
