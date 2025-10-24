import enum
import secrets
from dataclasses import dataclass

from sqlalchemy import Column, Enum, ForeignKey, String, Table, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.exceptions import (
    ReferralsFundValidationException,
    ReferralsJoinValidationException,
    ReferralsProjectValidationException,
)
from app.v1.dao.database import Base


def generate_short_key():
    return secrets.token_urlsafe(4)  # например:"aZ8kPq1L"


class ReferralTypeEnum(str, enum.Enum):
    JOIN = "join"
    FUND = "fund"
    PROJECT = "project"


referral_referees = Table(
    "referral_referees",
    Base.metadata,
    Column("referral_id", ForeignKey("referrals.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)


@dataclass
class Referral(Base):
    __tablename__ = "referrals"
    key: Mapped[str] = mapped_column(String(6), unique=True, default=generate_short_key, nullable=False)

    type: Mapped[ReferralTypeEnum] = mapped_column(Enum(ReferralTypeEnum), nullable=False)

    sharer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    sharer: Mapped["User"] = relationship("User", back_populates="referral_gens", lazy="selectin")  # noqa F821

    referees: Mapped[list["User"]] = relationship(  # noqa
        "User",
        secondary=referral_referees,
        back_populates="referral_uses",
        lazy="selectin",
    )

    fund_id: Mapped[int] = mapped_column(ForeignKey("funds.id"), nullable=True, index=True)
    fund: Mapped["Fund"] = relationship("Fund", back_populates="referrals", lazy="selectin")  # noqa F821

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=True, index=True)
    project: Mapped["Project"] = relationship("Project", back_populates="referrals", lazy="selectin")  # noqa F821

    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="referral", lazy="selectin")  # noqa F821
    recurring_payments: Mapped[list["RecurringPayment"]] = relationship(  # noqa: F821
        "RecurringPayment",
        back_populates="referral",
        lazy="selectin",
    )


@event.listens_for(Referral, "before_insert")
@event.listens_for(Referral, "before_update")
def validate_before_insert(mapper, connection, target):
    if target.type == ReferralTypeEnum.FUND and not target.fund_id:
        raise ReferralsFundValidationException

    if target.type == ReferralTypeEnum.PROJECT and not target.project_id:
        raise ReferralsProjectValidationException

    if target.type == ReferralTypeEnum.JOIN:
        if target.project_id or target.fund_id:
            raise ReferralsJoinValidationException
