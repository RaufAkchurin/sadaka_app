from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.v1.payment_yookassa.enums import ModelPaymentStatusEnum


class TBankPaymentMethodEnum(str, Enum):
    CARD = "card"
    SBP = "sbp"


class TBankCreatePaymentRequest(BaseModel):
    amount: int = Field(ge=100, description="Минимальная сумма платежа — 100 копеек")  # в копейках
    project_id: int


class TBankAddAccountQrRequest(BaseModel):
    description: str = Field(min_length=1, max_length=255)
    project_id: int

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Описание не может быть пустым.")
        return stripped


class TBankChargePaymentRequest(BaseModel):
    amount: int = Field(ge=100, description="Минимальная сумма платежа — 100 копеек")  # в копейках
    project_id: int
    rebill_id: int | str


class TBankChargeQrRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    amount: int = Field(ge=1000, description="Минимальная сумма платежа — 1000 копеек")
    project_id: int
    account_token: str = Field(min_length=1, max_length=255, alias="AccountToken")
    token: str = Field(min_length=1, max_length=255, alias="Token")

    @field_validator("account_token")
    @classmethod
    def validate_account_token(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Account token не может быть пустым.")
        return stripped


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
