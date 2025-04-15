import enum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dao.database import Base


class FileTypeEnum(enum.Enum):
    PDF = "PDF"


class Document(Base):
    name: Mapped[str]
    file_type: Mapped[FileTypeEnum] = mapped_column(
        SqlEnum(FileTypeEnum, name="doc_type_enum"),
        nullable=False,
    )
    size: Mapped[int]
    link: Mapped[str]

    funds: Mapped[list["Fund"]] = relationship("Fund", back_populates="document")  # noqa F821

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"


class Report(Base):
    name: Mapped[str]
    file_type: Mapped[FileTypeEnum] = mapped_column(
        SqlEnum(FileTypeEnum, name="doc_type_enum"),
        nullable=False,
    )
    size: Mapped[int]
    link: Mapped[str]

    projects: Mapped[list["Project"]] = relationship("Project", back_populates="report")  # noqa F821

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
