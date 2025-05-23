from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from v1.payment.enums import PaymentStatusEnum


class PaymentCreate(BaseModel):
    uuid: str
    status: PaymentStatusEnum
    currency: str
    amount: float
    income_amount: float
    balance_tokens: int
    payment_method: str
    created_at: datetime
    updated_at: datetime
    test: bool
    paid: bool
    confirmation_url: str
    description: Optional[str]


class PaymentResponse(BaseModel):
    uuid: str
    status: PaymentStatusEnum
    currency: str
    amount: float
    income_amount: float
    balance_tokens: int
    payment_method: str
    created_at: datetime
    updated_at: datetime
    test: bool
    paid: bool
    confirmation_url: str
    description: Optional[str]
