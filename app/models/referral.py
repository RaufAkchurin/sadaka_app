import enum
import secrets
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import TIMESTAMP, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.payment import Payment
from app.v1.dao.database import Base


def generate_short_key():
    return secrets.token_urlsafe(6)  # например: "aZ8kPq1L"


class ReferralTypeEnum(str, enum.Enum):
    JOIN = "join"
    FUND = "fund"
    PROJECT = "project"


@dataclass
class Referral(Base):
    entity_type: Mapped[ReferralTypeEnum] = mapped_column(Enum(ReferralTypeEnum), nullable=False)
    entity_id: Mapped[int] = mapped_column(nullable=True)

    key: Mapped[str] = mapped_column(
        String(20), primary_key=True, unique=True, default=generate_short_key, nullable=False
    )

    sharer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    sharer: Mapped["User"] = relationship("User", back_populates="referrals", lazy="joined")  # noqa F821

    payments: Mapped[list["Payment"]] = relationship(back_populates="referral")

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
