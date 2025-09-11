import enum
import secrets
from dataclasses import dataclass

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.v1.dao.database import Base


def generate_short_key():
    return secrets.token_urlsafe(4)  # например:"aZ8kPq1L"


class ReferralTypeEnum(str, enum.Enum):
    JOIN = "join"
    FUND = "fund"
    PROJECT = "project"


@dataclass
class Referral(Base):
    __tablename__ = "referrals"

    entity_type: Mapped[ReferralTypeEnum] = mapped_column(Enum(ReferralTypeEnum), nullable=False)

    fund_id: Mapped[int] = mapped_column(ForeignKey("funds.id"), nullable=True)
    fund: Mapped["Fund"] = relationship("Fund", back_populates="referrals", lazy="joined")  # noqa F821

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=True)
    project: Mapped["Project"] = relationship("Project", back_populates="referrals", lazy="joined")  # noqa F821

    key: Mapped[str] = mapped_column(String(6), unique=True, default=generate_short_key, nullable=False)

    sharer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    sharer: Mapped["User"] = relationship("User", back_populates="referrals", lazy="joined")  # noqa F821

    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="referral", lazy="joined")  # noqa F821

    # если тай то соответствующий инстанс наличие проверяем и от
