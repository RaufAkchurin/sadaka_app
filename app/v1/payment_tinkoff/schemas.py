from pydantic import BaseModel

from app.v1.payment_yookassa.enums import PaymentStatusEnum


class TBankCreatePaymentRequest(BaseModel):
    order_id: str
    amount: int  # в копейках
    description: str
    method: str | None = "card"  # card | sbp

    project_id: int


class TBankPayloadDataSchema(BaseModel):
    project_id: int


class TBankCallbackSchema(BaseModel):
    Success: bool
    Status: str
    PaymentId: int
    Amount: int

    Data: TBankPayloadDataSchema


class TBankPaymentCreateSchema(BaseModel):
    id: int

    user_id: int
    project_id: int
    stage_id: int

    amount: float
    income_amount: float

    status: PaymentStatusEnum = PaymentStatusEnum.PENDING
    # created_at: datetime
    # captured_at: datetime
    test: bool | None = False

    class Config:
        use_enum_values = True
