from pydantic import BaseModel

from app.v1.payment_yookassa.enums import ModelPaymentStatusEnum


class TBankCreatePaymentRequest(BaseModel):
    amount: int  # в копейках
    method: str | None = "card"  # card | sbp
    project_id: int


class TBankPayloadDataSchema(BaseModel):
    project_id: int
    user_id: int


class TBankCallbackSchema(BaseModel):
    Success: bool
    Status: str
    PaymentId: int
    Amount: int

    Data: TBankPayloadDataSchema


class PaymentByIdFilter(BaseModel):
    provider: str
    provider_payment_id: str
    status: ModelPaymentStatusEnum

    class Config:
        use_enum_values = True


class TBankSuccessPaymentCreateSchema(BaseModel):
    provider: str
    provider_payment_id: str

    user_id: int
    project_id: int
    stage_id: int

    amount: float
    status: ModelPaymentStatusEnum

    class Config:
        use_enum_values = True
