from dataclasses import dataclass

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.dao.database import Base
from app.file.enums import FileTypeEnum, MimeEnum
from app.utils.validators import validate_link_url


@dataclass
class File(Base):
    name: Mapped[str]
    size: Mapped[int]
    url: Mapped[str]
    type: Mapped[FileTypeEnum] = mapped_column(SqlEnum(FileTypeEnum, name="file_type_enum"), nullable=False)
    mime: Mapped[MimeEnum] = mapped_column(SqlEnum(MimeEnum, name="file_mime_enum"), nullable=False)

    # OneToOne
    user_picture: Mapped["User"] = relationship(  # noqa F821
        "User", back_populates="picture", cascade="all, delete-orphan", uselist=False
    )

    # OneToMany
    fund_id: Mapped[int | None] = mapped_column(ForeignKey("funds.id"), nullable=True)
    fund: Mapped["Fund"] = relationship("Fund", back_populates="documents")  # noqa F821

    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    project: Mapped["Project"] = relationship("Project", back_populates="documents")  # noqa F821

    stage_id: Mapped[int | None] = mapped_column(ForeignKey("stages.id"), nullable=True)
    stage: Mapped["Stage"] = relationship("Stage", back_populates="reports")  # noqa F821

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @validates("fund_id", "project_id", "stage_id", "user_picture")
    def validate_single_target(self, key, value):
        user_picture = 1 if key == "user_picture" else self.user_picture
        fund_id = value if key == "fund_id" else self.fund_id
        project_id = value if key == "project_id" else self.project_id
        stage_id = value if key == "stage_id" else self.stage_id

        ids = [fund_id, project_id, stage_id, user_picture]
        num_set = sum(bool(i) for i in ids)

        if num_set == 0:
            raise ValueError("File must be related to at least one model (project or fund).")
        if num_set > 1:
            raise ValueError(
                "File must be related to only one model (project or fund or stage or user_picture) not multiple."
            )

        return value

    @validates("url")
    def validate_link(self, key: str, value: str) -> str:
        return validate_link_url(value)

    @property
    def get_fullname(self):
        return self.name + "." + self.mime.value.lower()
