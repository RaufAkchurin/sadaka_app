import enum
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

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @validates("project_id", "fund_id", "report_id")
    def validate_single_target(self, key, value):
        # Используем "getattr" чтобы получить актуальные значения полей
        fund_id = value if key == "fund_id" else self.fund_id
        # project_id = value if key == "project_id" else self.project_id
        # report_id = value if key == "report_id" else self.report_id

        ids = [fund_id]
        num_set = sum(bool(i) for i in ids)

        if num_set == 0:
            raise ValueError("Document must be related to at least one model (project, fund, or report).")
        if num_set > 1:
            raise ValueError("Document must be related to only one model (not multiple).")

        return value

    @validates("url")
    def validate_link(self, key: str, value: str) -> str:
        return validate_link_url(value)


# class Report(Base):
#     name: Mapped[str]
#     file_type: Mapped[FileTypeEnum] = mapped_column(
#         SqlEnum(FileTypeEnum, name="doc_type_enum"),
#         nullable=False,
#     )
#     size: Mapped[int]
#     link: Mapped[str]
#
#     projects: Mapped[list["Project"]] = relationship("Project", back_populates="report")  # noqa F821
#
#     def __repr__(self):
#         return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
