from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InstanceIdFilterSchema(BaseModel):
    user_id: int | None = None
    project_id: int | None = None
    stage_id: int | None = None


class MyDonationSchema(BaseModel):
    project_name: str | None
    amount: float
    created_at: datetime
    # type: str                 #TODO after adding payment system change it

    model_config = ConfigDict(from_attributes=True)
