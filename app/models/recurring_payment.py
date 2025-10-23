from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.v1.dao.database import Base
from app.v1.payment_core.enums import PaymentMethodEnum, RecurringPaymentIntervalEnum, RecurringPaymentStatusEnum
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
        default=RecurringPaymentStatusEnum.PENDING,
        nullable=False,
        index=True,
    )
    payment_method: Mapped[PaymentMethodEnum] = mapped_column(
        SqlEnum(PaymentMethodEnum, name="payment_method_enum",),
        nullable=False,
        index=True,
    )

    interval: Mapped[RecurringPaymentIntervalEnum] = mapped_column(
        SqlEnum(RecurringPaymentIntervalEnum, name="recurring_payment_interval_enum"),
        default=RecurringPaymentIntervalEnum.MONTHLY,
        nullable=False,
    )

    amount: Mapped[float | None] = mapped_column(default=None)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)

    next_charge_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    last_charge_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retry_count: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    processing_task_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

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

    def mark_attempt(
        self,
        *,
        task_id: str | None = None,
        lock_expires_at: datetime | None = None,
    ) -> None:
        now = datetime.now(timezone.utc)
        self.last_attempt_at = now
        self.processing_task_id = task_id
        self.locked_until = lock_expires_at

    def mark_success(self, *, next_charge_at: datetime) -> None:
        now = datetime.now(timezone.utc)
        self.status = RecurringPaymentStatusEnum.ACTIVE
        self.last_charge_at = now
        self.last_attempt_at = now
        self.retry_count = 0
        self.next_charge_at = next_charge_at
        self.processing_task_id = None
        self.locked_until = None
        self.last_error = None

    def mark_failure(
        self,
        *,
        error: str,
        next_retry_at: datetime | None = None,
    ) -> None:
        now = datetime.now(timezone.utc)
        self.last_attempt_at = now
        self.last_error = error
        self.retry_count += 1
        self.processing_task_id = None
        self.locked_until = None

        if next_retry_at is not None:
            self.next_charge_at = next_retry_at

        if self.retry_count >= self.max_retry_count:
            self.status = RecurringPaymentStatusEnum.FAILED
        else:
            self.status = RecurringPaymentStatusEnum.PAST_DUE

    def reset_lock(self) -> None:
        self.processing_task_id = None
        self.locked_until = None

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id}, provider={self.provider}, interval={self.interval}, "
            f"status={self.status}, method={self.payment_method}, next_charge_at={self.next_charge_at}, user_id={self.user_id}, "
            f"project_id={self.project_id})"
        )
