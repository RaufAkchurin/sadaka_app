from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, event
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from app.v1.dao.database import Base


@dataclass
class OneTimePass(AsyncAttrs, DeclarativeBase):
    contact: Mapped[str] = mapped_column(String(11), unique=True, primary_key=True) # Phone or Email in Future

    code: Mapped[str | None] = mapped_column(String(6), nullable=True)
    expiration: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    count_of_request: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    count_of_confirmation: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    blocked_requests_until: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    blocked_confirmations_until: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)


#TODO Надо обнулять count_of_request и count_of_confirmation у всех каждые сколько то часов