from dataclasses import dataclass

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from v1.dao.database import Base
from v1.payment.enums import PaymentStatusEnum


@dataclass
class Payment(Base):
    # Core data
    amount: Mapped[float | None] = mapped_column(default=None)
    income_amount: Mapped[float | None] = mapped_column(default=None)
    test: Mapped[bool] = mapped_column(default=False)
    description: Mapped[str | None] = mapped_column(default=None)

    # With default values
    status: Mapped[PaymentStatusEnum] = mapped_column(
        SqlEnum(PaymentStatusEnum, name="payment_status_enum"), default=PaymentStatusEnum.PENDING
    )

    # Project relations
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="payments", lazy="joined")  # noqa F821

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    project: Mapped["Project"] = relationship("Project", back_populates="payments", lazy="joined")  # noqa F821

    stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"), nullable=False)
    stage: Mapped["Stage"] = relationship("Stage", back_populates="payments", lazy="joined")  # noqa F821

    def __str__(self):
        return f"{self.balance_tokens}, {self.status}"
