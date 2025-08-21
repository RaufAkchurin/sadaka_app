from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, event
from sqlalchemy.orm import Mapped, mapped_column

from app.v1.dao.database import Base


@dataclass
class OneTimePass(Base):
    phone: Mapped[str | None] = mapped_column(String(11), unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)

    code: Mapped[str | None] = mapped_column(String(6), nullable=True)
    expiration: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    count_of_request: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    count_of_confirmation: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    blocked_requests_until: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    blocked_confirmations_until: Mapped[datetime] = mapped_column(DateTime, nullable=True)


def _ensure_contact(mapper, connection, target: OneTimePass):
    """ORM-валидация перед INSERT/UPDATE: нужен хотя бы один из email/phone."""
    if not (target.email and target.email.strip()) and not (target.phone and target.phone.strip()):
        # Любое исключение прервёт flush/commit
        raise ValueError("У OneTimePass должен быть указан email или phone (хотя бы одно поле).")


# Подвязываем на insert/update
event.listen(OneTimePass, "before_insert", _ensure_contact)
event.listen(OneTimePass, "before_update", _ensure_contact)
