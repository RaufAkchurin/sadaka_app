from datetime import datetime

from pydantic import BaseModel

from app.v1.payment_yookassa.enums import PaymentStatusEnum


class TBankCreatePaymentRequest(BaseModel):
    order_id: str
    amount: int  # в копейках
    description: str
    method: str | None = "card"  # card | sbp


class TBankPayloadDataSchema(BaseModel):
    project_id: int | None = 1


class TBankCallbackSchema(BaseModel):
    Success: bool
    Status: str
    PaymentId: int
    Amount: int

    OrderId: str
    TerminalKey: str
    ErrorCode: str
    Token: str


class TBankPaymentCreateSchema(BaseModel):
    id: int

    amount: float
    income_amount: float
    status: PaymentStatusEnum = PaymentStatusEnum.PENDING

    created_at: datetime
    captured_at: datetime
    test: bool = True

    user_id: int
    project_id: int
    stage_id: int

    class Config:
        use_enum_values = True
