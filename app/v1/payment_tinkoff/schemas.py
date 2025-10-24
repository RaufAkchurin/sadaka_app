from enum import Enum

from pydantic import BaseModel, Field, field_validator
from app.v1.payment_yookassa.enums import ModelPaymentStatusEnum


class TBankPaymentMethodEnum(str, Enum):
    CARD = "card"
    SBP = "sbp"


class TBankCreatePaymentRequest(BaseModel):
    amount: int = Field(ge=1_000, description="Минимальная сумма платежа — 1000 копеек")  # в копейках
    method: TBankPaymentMethodEnum = TBankPaymentMethodEnum.CARD
    project_id: int


class TBankCreateRecurringPaymentRequest(TBankCreatePaymentRequest):
    method: TBankPaymentMethodEnum = Field(
        default=TBankPaymentMethodEnum.CARD,
        description="Для рекуррентного платежа доступны только операции по банковской карте",
    )

    @field_validator("method")
    @classmethod
    def ensure_card_method(cls, value: TBankPaymentMethodEnum) -> TBankPaymentMethodEnum:
        if value != TBankPaymentMethodEnum.CARD:
            raise ValueError("Рекуррентный платеж доступен только для метода card")
        return value


class TBankChargePaymentRequest(BaseModel):
    payment_id: int | str
    rebill_id: int | str


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
