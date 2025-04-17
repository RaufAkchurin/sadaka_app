# import enum
#
# from sqlalchemy import Enum as SqlEnum
# from sqlalchemy import ForeignKey, text
# from sqlalchemy.orm import Mapped, mapped_column, relationship
#
# from app.dao.database import Base
# from app.geo.models import Region
#
#
# class Project(Base):
#     name: Mapped[str]
#     description: Mapped[str | None]
#     picture: Mapped[str | None]
#
#     # region:
#     region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), default=1, server_default=text("1"))
#     region: Mapped["Region"] = relationship("Region", back_populates="regions", lazy="joined")
#
#     # # documents:
#     # document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
#     # document: Mapped["Document"] = relationship("Document", back_populates="documents", lazy="joined")
#     #
#     # # reports:
#     # report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"))
#     # report: Mapped["Report"] = relationship("Report", back_populates="reports", lazy="joined")
#
#     def __repr__(self):
#         return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
#
#
# class StageStatusEnum(enum.Enum):
#     ACTIVE = "active"
#     FINISHED = "finished"
#
#
# class Stage(Base):
#     name: Mapped[str]
#     status: Mapped[StageStatusEnum] = mapped_column(
#         SqlEnum(StageStatusEnum, name="doc_type_enum"),
#         nullable=False,
#     )
#     goal: Mapped[int]
#
#     # reports:
#     report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"))
#     report: Mapped["Report"] = relationship("Report", back_populates="reports", lazy="joined")
