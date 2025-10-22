from dataclasses import dataclass

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.v1.dao.database import Base
from app.v1.payment_core.enums import RecurringPaymentIntervalEnum, RecurringPaymentStatusEnum
from app.v1.payment_yookassa.enums import PaymentProviderEnum


@dataclass
class RecurringPayment(Base):
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_rebill_id",
            name="uq_recurring_payments_provider_rebill_id",
        ),
    )

    provider: Mapped[PaymentProviderEnum] = mapped_column(
        SqlEnum(PaymentProviderEnum, name="recurring_payment_provider_enum"),
        default=PaymentProviderEnum.TBANK.value,
        nullable=False,
        index=True,
    )
    provider_rebill_id: Mapped[str] = mapped_column(nullable=False)
    provider_card_id: Mapped[str | None] = mapped_column(nullable=True)

    status: Mapped[RecurringPaymentStatusEnum] = mapped_column(
        SqlEnum(RecurringPaymentStatusEnum, name="recurring_payment_status_enum"),
        default=RecurringPaymentStatusEnum.ACTIVE,
        nullable=False,
        index=True,
    )

    interval: Mapped[RecurringPaymentIntervalEnum] = mapped_column(
        SqlEnum(RecurringPaymentIntervalEnum, name="recurring_payment_interval_enum"),
        default=RecurringPaymentIntervalEnum.MONTHLY,
        nullable=False,
    )

    amount: Mapped[float | None] = mapped_column(default=None)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = relationship("User", back_populates="recurring_payments", lazy="selectin")  # noqa: F821

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    project: Mapped["Project"] = relationship(  # noqa: F821
        "Project",
        back_populates="recurring_payments",
        lazy="selectin",
    )

    stage_id: Mapped[int | None] = mapped_column(ForeignKey("stages.id"), nullable=True, index=True)
    stage: Mapped["Stage"] = relationship("Stage", back_populates="recurring_payments", lazy="noload")  # noqa: F821

    referral_id: Mapped[int | None] = mapped_column(
        ForeignKey("referrals.id", name="fk_recurring_payments_referral_id"),
        nullable=True,
        default=None,
        index=True,
    )
    referral: Mapped["Referral"] = relationship(  # noqa: F821
        "Referral",
        back_populates="recurring_payments",
        lazy="noload",
    )

    payments: Mapped[list["Payment"]] = relationship(  # noqa: F821
        "Payment",
        back_populates="recurring_payment",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id}, provider={self.provider}, interval={self.interval}, "
            f"status={self.status}, user_id={self.user_id}, project_id={self.project_id})"
        )
