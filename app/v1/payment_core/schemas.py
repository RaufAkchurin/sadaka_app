from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InstanceIdFilterSchema(BaseModel):
    user_id: int | None = None
    project_id: int | None = None
    stage_id: int | None = None


class BaseDonationSchema(BaseModel):
    amount: float
    created_at: datetime

    # TODO type: str                 #TODO after adding payment system change it
    model_config = ConfigDict(from_attributes=True)


class UserDonationSchema(BaseDonationSchema):
    project_name: str | None


class ProjectDonationSchema(BaseDonationSchema):
    donor_name: str
