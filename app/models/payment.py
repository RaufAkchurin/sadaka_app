from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy import TIMESTAMP
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.v1.dao.database import Base
from app.v1.payment_yookassa.enums import PaymentStatusEnum


class PaymentProvider(str, Enum):
    YOOKASSA = "yookassa"
    TBANK = "tbank"


@dataclass
class Payment(Base):
    # Provider specific data
    provider: Mapped[PaymentProvider] = mapped_column(
        SqlEnum(PaymentProvider, name="payment_provider_enum"), default=PaymentProvider.TBANK, index=True
    )
    provider_payment_id: Mapped[str] = mapped_column(nullable=False)

    # Base info
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    captured_at: Mapped[datetime] = mapped_column(TIMESTAMP)

    # Core data
    amount: Mapped[float | None] = mapped_column(default=None)
    income_amount: Mapped[float | None] = mapped_column(default=None)  # Only for YOOKASSA
    test: Mapped[bool] = mapped_column(default=False)

    # With default values
    status: Mapped[PaymentStatusEnum] = mapped_column(
        SqlEnum(PaymentStatusEnum, name="payment_status_enum"), default=PaymentStatusEnum.PENDING, index=True
    )

    # Project relations
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = relationship("User", back_populates="payments", lazy="selectin")  # noqa F821

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    project: Mapped["Project"] = relationship("Project", back_populates="payments", lazy="selectin")  # noqa F821

    stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"), nullable=False, index=True)
    stage: Mapped["Stage"] = relationship("Stage", back_populates="payments", lazy="noload")  # noqa F821

    referral_id: Mapped[int | None] = mapped_column(
        ForeignKey("referrals.id", name="fk_payments_referral_id"), nullable=True, default=None, index=True
    )
    referral: Mapped["Referral"] = relationship("Referral", back_populates="payments", lazy="noload")  # noqa F821

    def __str__(self):
        return f"{self.id}, {self.income_amount}, {self.status}, test - {self.test}"

    @property
    def project_name(self) -> str | None:
        return self.project.name if self.project else None

    @property
    def donor_name(self) -> str | None:
        return self.user.name if self.user else None
