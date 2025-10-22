from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.v1.payment_core.enums import PaymentMethodEnum, RecurringPaymentIntervalEnum, RecurringPaymentStatusEnum


class InstanceIdFilterSchema(BaseModel):
    user_id: int | None = None
    project_id: int | None = None
    stage_id: int | None = None


class RecurringPaymentFilterSchema(BaseModel):
    user_id: int | None = None
    project_id: int | None = None
    status: RecurringPaymentStatusEnum | None = None
    interval: RecurringPaymentIntervalEnum | None = None
    payment_method: PaymentMethodEnum | None = None

    model_config = ConfigDict(use_enum_values=True)


class BaseDonationSchema(BaseModel):
    amount: float
    created_at: datetime
    type: str
    model_config = ConfigDict(from_attributes=True)


class UserDonationSchema(BaseDonationSchema):
    project_name: str | None


class ProjectDonationSchema(BaseDonationSchema):
    donor_name: str
