from dataclasses import dataclass

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from v1.dao.database import Base
from v1.payment.enums import PaymentStatusEnum


@dataclass
class Payment(Base):
    # Core data
    currency: Mapped[str]
    amount: Mapped[float | None] = mapped_column(default=None)
    income_amount: Mapped[float | None] = mapped_column(default=None)
    balance_tokens: Mapped[int] = mapped_column(default=0)
    payment_method: Mapped[str | None] = mapped_column(default=None)
    test: Mapped[bool] = mapped_column(default=False)
    paid: Mapped[bool] = mapped_column(default=False)
    confirmation_url: Mapped[str | None] = mapped_column(default=None)
    description: Mapped[str | None] = mapped_column(default=None)

    # With default values
    uuid: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[PaymentStatusEnum] = mapped_column(
        SqlEnum(PaymentStatusEnum, name="payment_status_enum"), default=PaymentStatusEnum.PENDING
    )

    # Project relations
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="payments", lazy="joined")

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    project: Mapped["Project"] = relationship("Project", back_populates="payments", lazy="joined")

    stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"), nullable=False)
    stage: Mapped["Stage"] = relationship("Stage", back_populates="payments", lazy="joined")

    def __str__(self):
        return f"{self.balance_tokens}, {self.status}"


# @dataclass
# class Payment(Base):
#     amount: Mapped[int]
#
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
#     user: Mapped["User"] = relationship("User", back_populates="payments", lazy="joined")  # noqa: F821
#
#     project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
#     project: Mapped["Project"] = relationship("Project", back_populates="payments", lazy="joined")  # noqa: F821
#
#     stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"), nullable=False)
#     stage: Mapped["Stage"] = relationship("Stage", back_populates="payments", lazy="joined")  # noqa: F821
#
#     def __repr__(self):
#         return f"{self.__class__.__name__}(id={self.id}, project={self.project_id}, amount={self.amount})"
