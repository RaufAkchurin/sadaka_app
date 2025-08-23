from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints

from app.v1.api_utils.validators import validate_phone

PhoneE164_RUS = Annotated[
    str,
    StringConstraints(pattern=r"^\+7\d{10}$", min_length=12, max_length=12),
    # FOR view correct phone number in docs when trying
    AfterValidator(validate_phone),
]


class OtpPhoneOnlySchema(BaseModel):
    phone: PhoneE164_RUS
    model_config = ConfigDict(from_attributes=True)


class OtpCodeAddSchema(OtpPhoneOnlySchema):
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$", description="Код подтверждения в формате 123456")
    expiration: datetime = Field()


class OtpCodeCheckSchema(OtpPhoneOnlySchema):
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$", description="Код подтверждения в формате 123456")


class OtpBlockedRequestAddSchema(OtpCodeAddSchema):
    blocked_requests_until: datetime = Field()


class OtpBlockedConfirmationsAddSchema(OtpCodeAddSchema):
    blocked_confirmations_until: datetime = Field()
