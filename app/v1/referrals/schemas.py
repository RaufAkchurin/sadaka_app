import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.models.referral import ReferralTypeEnum


class ReferralKeyResponseSchema(BaseModel):
    key: str
    model_config = ConfigDict(from_attributes=True)


class ReferralAddSchema(BaseModel):
    type: ReferralTypeEnum
    sharer_id: int

    created_at: datetime.datetime | None = datetime.datetime.now()
    fund_id: int | None = None
    project_id: int | None = None


class ReferralDonationsSchema(BaseModel):
    id: int
    referral_income: float
    referral_donors_count: int

    created_at: datetime.datetime = Field(exclude=True)  # (для расчета количества дней)
    # raw related models (не сериализуются, нужны только для доступа)
    fund: object | None = Field(default=None, exclude=True)
    project: object | None = Field(default=None, exclude=True)

    @computed_field
    @property
    def fund_name(self) -> str | None:
        return self.fund.name if self.fund else None

    @computed_field
    @property
    def project_name(self) -> str | None:
        return self.project.name if self.project else None

    @computed_field
    @property
    def days_after_created(self) -> int:
        created_at_date = self.created_at
        days_after_created = (datetime.datetime.now() - created_at_date).days
        return days_after_created

    model_config = ConfigDict(from_attributes=True)
