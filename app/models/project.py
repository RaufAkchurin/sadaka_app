from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.file import File
from app.models.fund import Fund
from app.models.referral import Referral
from app.v1.dao.database import Base
from app.v1.project.enums import AbstractStatusEnum
from app.v1.project.schemas import RegionInfoSchema


class Project(Base):
    # TODO имей ввиду что нигде нет проверки на наличие картинок у проекта, валидации не работают
    name: Mapped[str]
    status: Mapped[AbstractStatusEnum] = mapped_column(
        SqlEnum(AbstractStatusEnum, name="project_status_enum"),
        nullable=False,
        index=True,
    )

    # TODO add chars max value
    description: Mapped[str | None]
    goal: Mapped[int]

    fund_id: Mapped[int] = mapped_column(ForeignKey("funds.id"), nullable=False, index=True)
    fund: Mapped["Fund"] = relationship("Fund", back_populates="projects", lazy="noload")

    documents: Mapped[list["File"]] = relationship(  # noqa: F821
        "File",
        back_populates="project_document",
        cascade="all, delete-orphan",
        foreign_keys="[File.project_document_id]",
        lazy="noload",
    )

    pictures: Mapped[list["File"]] = relationship(  # noqa: F821
        "File",
        back_populates="project_picture",
        cascade="all, delete-orphan",
        foreign_keys=[File.project_picture_id],
        lazy="noload",
    )

    stages: Mapped[list["Stage"]] = relationship(  # noqa: F821
        "Stage", back_populates="project", cascade="all, delete-orphan", lazy="noload"
    )

    payments: Mapped[list["Payment"]] = relationship(  # noqa: F821
        "Payment", back_populates="project", cascade="all, delete-orphan", lazy="noload"
    )

    comments: Mapped[list["Comment"]] = relationship(  # noqa: F821
        "Comment", back_populates="project", cascade="all, delete-orphan", lazy="noload"
    )

    referrals: Mapped[list["Referral"]] = relationship(  # noqa: F821
        "Referral", back_populates="project", cascade="all, delete-orphan", lazy="noload"
    )

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @property
    def region(self) -> RegionInfoSchema:
        region_name = ""
        region_picture_url = ""

        if self.fund and self.fund.region and self.fund.region.picture:
            region_picture_url = self.fund.region.picture.url

        if self.fund and self.fund.region and self.fund.region.name:
            region_name = self.fund.region.name

        region_info = RegionInfoSchema.model_validate({"name": region_name, "picture_url": region_picture_url})

        return region_info

    @validates("documents")
    def validate_documents_count(self, key, document):
        if len(self.documents) >= 5:
            raise ValueError("You can't have more than 5 documents.")
        return document

    @property
    def active_stage_number(self) -> Mapped[int] | None:
        stages = self.stages
        active_stage = None
        for stage in stages:
            if stage.status.value == "active":
                active_stage = stage
                break
        if active_stage is None:
            return None
        return active_stage.number

    @property
    def pictures_list(self) -> list[str]:
        pictures = self.pictures
        urls_list = []
        for picture in pictures:
            urls_list.append(picture.url)
        return urls_list

    @property
    def total_income(self) -> float:
        return sum(payment.income_amount for payment in self.payments)

    @property
    def collected_percentage(self) -> int:
        collected_percentage = int((self.total_income / self.goal) * 100) if self.goal > 0 else 0
        return collected_percentage

    @property
    def unique_sponsors(self) -> int:
        unique_sponsors = set()
        for payment in self.payments:
            unique_sponsors.add(payment.user_id)
        return len(unique_sponsors)
