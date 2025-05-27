from datetime import datetime

from pydantic import BaseModel
from pydantic_core import Url
from v1.payment.enums import PaymentStatusEnum


class PaymentCreateSchema(BaseModel):
    amount: float | None = 0
    income_amount: float | None = 0
    test: bool = True
    status: PaymentStatusEnum = PaymentStatusEnum.PENDING
    user_id: int
    project_id: int
    stage_id: int

    class Config:
        use_enum_values = True


class PaymentStatusUpdateSchema(BaseModel):
    status: PaymentStatusEnum = PaymentStatusEnum.PENDING


class YooPaymentUrlSchema(BaseModel):
    redirect_url: Url


class YooPaymentIdFilter(BaseModel):
    id: int


class YooAmount(BaseModel):
    currency: str
    value: str


class YooThreeDSecure(BaseModel):
    applied: bool
    challenge_completed: bool
    method_completed: bool


class YooAuthorizationDetails(BaseModel):
    auth_code: str
    rrn: str
    three_d_secure: YooThreeDSecure


class YooMetadataInputSchema(BaseModel):
    payment_id: str
    project_id: str
    user_id: str


class YooMetadataCallbackSchema(BaseModel):
    payment_id: int
    project_id: int
    user_id: int


class YooWebhookDataSchema(BaseModel):
    amount: YooAmount
    authorization_details: YooAuthorizationDetails
    captured_at: datetime
    created_at: datetime
    description: str
    id: str
    income_amount: YooAmount
    metadata: YooMetadataCallbackSchema
    paid: bool
    status: str
    test: bool
