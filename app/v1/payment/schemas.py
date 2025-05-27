from datetime import datetime

from pydantic import BaseModel
from v1.payment.enums import PaymentStatusEnum


class PaymentCreateSchema(BaseModel):
    amount: float | None = 0
    income_amount: float | None = 0
    test: bool = True
    description: str | None = ""
    status: PaymentStatusEnum = PaymentStatusEnum.PENDING
    user_id: int
    project_id: int
    stage_id: int

    class Config:
        use_enum_values = True


class PaymentStatusUpdateSchema(BaseModel):
    status: PaymentStatusEnum = PaymentStatusEnum.PENDING


class PaymentIdFilter(BaseModel):
    id: int


class Amount(BaseModel):
    currency: str
    value: str


class ThreeDSecure(BaseModel):
    applied: bool
    challenge_completed: bool
    method_completed: bool


class AuthorizationDetails(BaseModel):
    auth_code: str
    rrn: str
    three_d_secure: ThreeDSecure


class Metadata(BaseModel):
    payment_id: int
    project_id: int
    user_id: int


class WebhookData(BaseModel):
    amount: Amount
    authorization_details: AuthorizationDetails
    captured_at: datetime
    created_at: datetime
    description: str
    id: str
    income_amount: Amount
    metadata: Metadata
    paid: bool
    status: str
    test: bool
