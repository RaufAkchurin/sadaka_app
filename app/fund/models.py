from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dao.database import Base
from app.documents.models import Document
from app.geo.models import Region


class Fund(Base):
    name: Mapped[str]
    description: Mapped[str | None]
    picture: Mapped[str | None]

    # region:
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), default=1, server_default=text("1"))
    region: Mapped["Region"] = relationship("Region", back_populates="regions", lazy="joined")

    # documents:
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    document: Mapped["Document"] = relationship("Document", back_populates="documents", lazy="joined")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
