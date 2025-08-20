from dataclasses import dataclass

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.v1.dao.database import Base


@dataclass
class OneTimePass(Base):
    # - One-Time Password for registrations
    # - Without validation for phone or email existing because it in router sms/registration

    phone: Mapped[str | None] = mapped_column(String(11), nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    code: Mapped[str] = mapped_column(String(6), nullable=False)
