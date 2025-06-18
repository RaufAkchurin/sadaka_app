from dataclasses import dataclass

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, event
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from v1.api_utils.validators import validate_link_url
from v1.dao.database import Base
from v1.file.enums import FileTypeEnum, MimeEnum


@dataclass
class File(Base):
    name: Mapped[str]
    size: Mapped[int]
    url: Mapped[str]
    type: Mapped[FileTypeEnum] = mapped_column(SqlEnum(FileTypeEnum, name="file_type_enum"), nullable=False)
    mime: Mapped[MimeEnum] = mapped_column(SqlEnum(MimeEnum, name="file_mime_enum"), nullable=False)

    # OneToOne
    user_picture: Mapped["User"] = relationship(  # noqa F821
        "User", back_populates="picture", uselist=False, passive_deletes=True
    )

    region: Mapped["Region"] = relationship(  # noqa F821
        "Region", back_populates="picture", uselist=False, passive_deletes=True
    )

    fund_picture: Mapped["Fund"] = relationship(  # noqa F821
        "Fund", back_populates="picture", foreign_keys="[Fund.picture_id]", uselist=False, passive_deletes=True
    )

    # OneToMany
    fund_document_id: Mapped[int | None] = mapped_column(ForeignKey("funds.id"), nullable=True)
    fund_document: Mapped["Fund"] = relationship(  # noqa F821
        "Fund",
        back_populates="documents",
        foreign_keys=[fund_document_id],
    )

    project_document_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    project_document: Mapped["Project"] = relationship(  # noqa F821
        "Project", back_populates="documents", foreign_keys="[File.project_document_id]"
    )

    project_picture_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    project_picture: Mapped["Project"] = relationship(  # noqa F821
        "Project", back_populates="pictures", foreign_keys="[File.project_picture_id]"
    )

    stage_id: Mapped[int | None] = mapped_column(ForeignKey("stages.id"), nullable=True)
    stage: Mapped["Stage"] = relationship("Stage", back_populates="reports")  # noqa F821

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @validates("url")
    def validate_link(self, key: str, value: str) -> str:
        return validate_link_url(value)

    @property
    def get_fullname(self):
        return self.name + "." + self.mime.value.lower()

    @property
    def picture_url(self) -> str | None:
        return self.url

    @property
    def upload(self):  # this method for sqladmin update method without uploaded picture
        return None

    def count_non_null_relations(self) -> int:
        count = 0
        if self.user_picture is not None:
            count += 1
        if self.region is not None:
            count += 1
        if self.fund_picture is not None:
            count += 1
        if self.fund_document is not None:
            count += 1
        if self.project_document is not None:
            count += 1
        if self.project_picture is not None:
            count += 1
        if self.stage is not None:
            count += 1
        return count

    def validate_one_relation(self):
        count = self.count_non_null_relations()
        if count != 1:
            raise ValueError(
                "File must be linked to exactly ONE related model (User, Region, Fund, Project, Stage). "
                f"Found {count} linked."
            )


@event.listens_for(File, "before_insert")
@event.listens_for(File, "before_update")
def receive_before_insert_or_update(mapper, connection, target):
    target.validate_one_relation()
