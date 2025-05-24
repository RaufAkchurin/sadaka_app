from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, HttpUrl
from v1.payment.enums import PaymentStatusEnum


class Amount(BaseModel):
    value: Decimal
    currency: str


class Confirmation(BaseModel):
    type: str
    confirmation_url: HttpUrl


class Recipient(BaseModel):
    account_id: str
    gateway_id: str


class YookassaResponse(BaseModel):
    id: str
    status: str
    paid: bool
    amount: Amount
    confirmation: Confirmation
    created_at: datetime
    description: str
    metadata: dict
    recipient: Recipient
    refundable: bool
    test: bool


class PaymentCreate(BaseModel):
    uuid: str
    status: PaymentStatusEnum
    currency: str
    amount: float
    income_amount: float
    # balance_tokens: int
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
    # balance_tokens: int
    payment_method: str
    created_at: datetime
    updated_at: datetime
    test: bool
    paid: bool
    confirmation_url: str
    description: Optional[str]
