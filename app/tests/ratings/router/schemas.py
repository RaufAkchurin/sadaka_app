import datetime
import uuid

from pydantic import BaseModel


class TestPaymentAddSchema(BaseModel):
    id: uuid.UUID
    user_id: int
    project_id: int
    stage_id: int
    referral_id: int | None = None
    amount: float | None = None
    income_amount: float = 0.0
    created_at: datetime.datetime | None = datetime.datetime.now()  # передавать значения всеравно приходится(
    updated_at: datetime.datetime | None = datetime.datetime.now()
    captured_at: datetime.datetime | None = datetime.datetime.now()
