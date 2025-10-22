from dataclasses import dataclass

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.v1.dao.database import Base
from app.v1.payment_yookassa.enums import ModelPaymentStatusEnum, PaymentProviderEnum


@dataclass
class Payment(Base):
    # Constraints
    __table_args__ = (
        UniqueConstraint("provider", "provider_payment_id", name="uq_payments_provider_payment_id"),
    )  # provider_payment_id unique for provider

    # Provider specific data
    provider: Mapped[PaymentProviderEnum] = mapped_column(
        SqlEnum(PaymentProviderEnum, name="payment_provider_enum"), default=PaymentProviderEnum.TBANK.value, index=True
    )
    provider_payment_id: Mapped[str] = mapped_column(nullable=False)

    # Core data
    amount: Mapped[float | None] = mapped_column(default=None)
    income_amount: Mapped[float | None] = mapped_column(default=None)  # Only for YOOKASSA
    test: Mapped[bool] = mapped_column(default=False)

    # With default values
    status: Mapped[ModelPaymentStatusEnum] = mapped_column(
        SqlEnum(ModelPaymentStatusEnum, name="payment_status_enum"), default=ModelPaymentStatusEnum.PENDING, index=True
    )

    # Project relations
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = relationship("User", back_populates="payments", lazy="selectin")  # noqa F821

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    project: Mapped["Project"] = relationship("Project", back_populates="payments", lazy="selectin")  # noqa F821

    stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"), nullable=True, index=True)
    stage: Mapped["Stage"] = relationship("Stage", back_populates="payments", lazy="noload")  # noqa F821

    referral_id: Mapped[int | None] = mapped_column(
        ForeignKey("referrals.id", name="fk_payments_referral_id"), nullable=True, default=None, index=True
    )
    referral: Mapped["Referral"] = relationship("Referral", back_populates="payments", lazy="noload")  # noqa F821

    recurring_payment_id: Mapped[int | None] = mapped_column(
        ForeignKey("recurringpayments.id", name="fk_payments_recurring_payment_id"),
        nullable=True,
        default=None,
        index=True,
    )
    recurring_payment: Mapped["RecurringPayment"] = relationship(  # noqa: F821
        "RecurringPayment",
        back_populates="payments",
        lazy="noload",
    )

    def __str__(self):
        return f"{self.id}, {self.amount}, {self.status}, test - {self.test}"

    @property
    def project_name(self) -> str | None:
        return self.project.name if self.project else None

    @property
    def donor_name(self) -> str | None:
        return self.user.name if self.user else None
