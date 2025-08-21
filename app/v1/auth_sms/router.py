import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import CodeExpiredException, CodeWrongException, \
    CodeRequestBlockerException
from app.models.one_time_pass import OneTimePass
from app.models.user import User
from app.v1.auth.service_auth import set_tokens_to_response
from app.v1.auth_sms.schemas import OtpAddSchema, OtpPhoneOnlySchema, OtpCodeCheckSchema
from app.v1.auth_sms.service_smsc import SMSC
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.users.dao import UserDAO, OneTimePassDAO
from app.v1.users.schemas import UserPhoneOnlySchema

v1_auth_sms_router = APIRouter()

@v1_auth_sms_router.post("/send_code/")
async def send_sms(
    user_data: OtpPhoneOnlySchema,
    session: AsyncSession = Depends(get_session_with_commit),
):

    otp_dao = OneTimePassDAO(session)
    new_code = random.randint(100000, 999999)
    new_expiration = datetime.now() + timedelta(minutes=5)
    max_requests_count = 2

    otp: OneTimePass = await otp_dao.find_one_or_none(filters=OtpPhoneOnlySchema(phone=user_data.phone))


    if otp is None:
        await otp_dao.add(OtpAddSchema(
                phone=user_data.phone,
                code=str(new_code),
                expiration=new_expiration
        ))

    else:
        otp.count_of_request += 1
        otp.code = new_code
        otp.expiration = new_expiration

    if otp.count_of_request > max_requests_count:
        otp.blocked_requests_until = datetime.now() + timedelta(hours=4)

    if otp.blocked_requests_until > datetime.now():
        raise CodeRequestBlockerException

    smsc = SMSC()
    smsc.send_sms(user_data.phone[1:], f"Код подтверждения: {new_code}", sender="sms")

    return {"message": "Код подтверждения успешно отправлен."}



@v1_auth_sms_router.post("/check_code/")
async def check_code_from_sms(
    response: Response,
    check_code_data: OtpCodeCheckSchema,
    session: AsyncSession = Depends(get_session_with_commit),
) -> dict | None:

    max_confirmation_count = 5

    user_dao = UserDAO(session)
    otp_dao = OneTimePassDAO(session)

    user:User = await user_dao.find_one_or_none(filters=OtpPhoneOnlySchema(phone=check_code_data.phone))
    otp:OneTimePass  = await otp_dao.find_one_or_none(filters=OtpPhoneOnlySchema(phone=check_code_data.phone))

    if otp.blocked_confirmations_until < datetime.now():
        raise CodeWrongException

        # проверка кода подтверждения
    if otp.code != check_code_data.code:
        otp.count_of_confirmation += 1

        # блокировка возможности подтвердить смс
    if otp.count_of_confirmation >= max_confirmation_count:
        otp.blocked_confirmations_until = datetime.now() + timedelta(hours=4)
        raise CodeWrongException

        # проверка срока жизни
    if datetime.now() >= otp.expiration:
        raise CodeExpiredException

        # успех
    if user is not None:
        await otp.clear_data()

    else:
        user = await user_dao.add(UserPhoneOnlySchema(phone=check_code_data.phone))

    set_tokens_to_response(response, user)
    return {"message": "Вы успешно авторизованы."}


