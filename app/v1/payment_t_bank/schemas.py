# models.py
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CreatePaymentRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Сумма платежа")
    currency: str = Field(default="RUB", description="Валюта")
    order_id: str = Field(..., description="ID заказа в вашей системе")
    description: str = Field(..., description="Описание платежа")
    user_id: str = Field(..., description="ID пользователя")
    card_token: Optional[str] = Field(None, description="Токен карты для повторных платежей")


class PaymentResponse(BaseModel):
    payment_id: str
    status: PaymentStatus
    payment_url: Optional[str] = None
    amount: float
    order_id: str
    created_at: datetime


class WebhookData(BaseModel):
    payment_id: str
    order_id: str
    status: PaymentStatus
    amount: float
    currency: str
    transaction_id: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime


class TBankPaymentRequest(BaseModel):
    MerchantID: str
    TerminalID: str
    Amount: str
    Currency: str
    OrderID: str
    Description: str
    SuccessURL: Optional[str] = None
    FailURL: Optional[str] = None


class TBankPaymentResponse(BaseModel):
    Success: bool
    PaymentID: Optional[str] = None
    PaymentURL: Optional[str] = None
    ErrorCode: Optional[str] = None
    ErrorMessage: Optional[str] = None
