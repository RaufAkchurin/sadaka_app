from datetime import datetime

from pydantic import Field

from app.v1.auth_sms.schemas import OtpCodeAddSchema


class OtpBlockedRequestAddSchema(OtpCodeAddSchema):
    blocked_requests_until: datetime = Field()
    count_of_request: int = Field()


class OtpBlockedConfirmationsAddSchema(OtpCodeAddSchema):
    blocked_confirmations_until: datetime = Field()
    count_of_confirmation: int = Field()
