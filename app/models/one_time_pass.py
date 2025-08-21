from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from app.v1.dao.database import Base


@dataclass
class OneTimePass(Base):
    phone: Mapped[str] = mapped_column(String(11), unique=True, nullable=True)

    code: Mapped[str | None] = mapped_column(String(6), nullable=True)
    expiration: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    count_of_request: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    count_of_confirmation: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    blocked_requests_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)
    blocked_confirmations_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)


#TODO Надо обнулять count_of_request и count_of_confirmation у всех каждые сколько то часов

    async def clear_data(self):
        self.code = None
        self.expiration = None
        self.blocked_confirmations_until = None
        self.blocked_requests_until = None
        self.count_of_confirmation = 0
        self.count_of_request = 0
        return self