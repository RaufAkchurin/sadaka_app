from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.v1.users.schemas import PhoneE164_RUS


class OtpSearchSchema(BaseModel):
    phone: Optional[str] = PhoneE164_RUS
    model_config = ConfigDict(from_attributes=True)


class OtpAddSchema(BaseModel):
    phone: Optional[str] = PhoneE164_RUS
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$", description="Код подтверждения в формате 123456")
    expiration: datetime = Field()