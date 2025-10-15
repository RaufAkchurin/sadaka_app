from enum import Enum

from pydantic import BaseModel
from app.v1.payment_yookassa.enums import ModelPaymentStatusEnum


class TBankPaymentMethodEnum(str, Enum):
    CARD = "card"
    SBP = "sbp"


class TBankCreatePaymentRequest(BaseModel):
    amount: int  # в копейках
    method: TBankPaymentMethodEnum = TBankPaymentMethodEnum.CARD
    project_id: int
    recurring: bool = False


class TBankPayloadDataSchema(BaseModel):
    project_id: int
    user_id: int
    is_recurring: bool | None = False


class TBankCallbackSchema(BaseModel):
    Success: bool
    Status: str
    PaymentId: int
    Amount: int
    RebillId: int | str | None = None
    CardId: int | str | None = None

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
