import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import CodeExpiredException, CodeNotFoundedException, CodeWrongException
from app.v1.auth.service_auth import set_tokens_to_response
from app.v1.auth_sms.service_smsc import SMSC
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.users.dao import UserDAO
from app.v1.users.schemas import UserCodeAddSchema, UserCodeCheckSchema, UserPhoneOnlySchema

v1_auth_sms_router = APIRouter()


@v1_auth_sms_router.post("/send_code/")
async def send_sms(
    user_data: UserPhoneOnlySchema,
    session: AsyncSession = Depends(get_session_with_commit),
) -> dict:
    user_dao = UserDAO(session)
    confirmation_code = random.randint(100000, 999999)

    old_user = await user_dao.find_one_or_none(filters=UserPhoneOnlySchema(phone=user_data.phone))
    if old_user is None:
        await user_dao.add(
            UserCodeAddSchema(
                phone=user_data.phone,
                confirmation_code=confirmation_code,
                confirmation_code_expiry=datetime.now() + timedelta(minutes=5),
                is_active=False,  # To be active after code positive confirmation
            )
        )
    else:
        old_user.confirmation_code = confirmation_code
        old_user.confirmation_code_expiry = datetime.now() + timedelta(minutes=5)

    smsc = SMSC()
    smsc.send_sms(user_data.phone[1:], f"Код подтверждения: {confirmation_code}", sender="sms")

    return {"message": "Code sent"}


@v1_auth_sms_router.post("/check_code/")
async def check_code_from_sms(
    response: Response,
    user_data: UserCodeCheckSchema,
    session: AsyncSession = Depends(get_session_with_commit),
) -> dict | None:
    user_dao = UserDAO(session)
    user_by_phone = await user_dao.find_one_or_none(filters=UserPhoneOnlySchema(phone=user_data.phone))

    if user_by_phone is not None and user_by_phone.confirmation_code == user_data.confirmation_code:
        if hasattr(user_by_phone, "confirmation_code") and hasattr(user_by_phone, "confirmation_code_expiry"):
            if datetime.now() < user_by_phone.confirmation_code_expiry:
                user_by_phone.is_active = True
                set_tokens_to_response(response, user_by_phone)
                return {"message": "Вы успешно авторизованы."}
            else:
                raise CodeExpiredException
        else:
            raise CodeNotFoundedException
    else:
        raise CodeWrongException
