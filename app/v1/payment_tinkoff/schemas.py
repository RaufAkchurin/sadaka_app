from pydantic import BaseModel

from app.v1.payment_yookassa.enums import PaymentProviderEnum, PaymentStatusEnum


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


class TBankSuccessPaymentCreateSchema(BaseModel):
    provider: PaymentProviderEnum
    provider_payment_id: str

    user_id: int
    project_id: int
    stage_id: int

    amount: float
    status: PaymentStatusEnum = PaymentStatusEnum.SUCCEEDED

    class Config:
        use_enum_values = True
