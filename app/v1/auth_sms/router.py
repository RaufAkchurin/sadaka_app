import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1.auth_sms.service_smsc import SMSC
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.users.dao import UserDAO
from app.v1.users.schemas import UserAddWithCodeSchema, UserPhoneOnlySchema

v1_auth_sms_router = APIRouter(tags=["Auth v1"])


@v1_auth_sms_router.post("/send_code/")
async def register_by_sms(
    response: Response,
    user_data: UserPhoneOnlySchema,
    session: AsyncSession = Depends(get_session_with_commit),
) -> dict:
    user_dao = UserDAO(session)
    confirmation_code = random.randint(100000, 999999)

    old_user = await user_dao.find_one_or_none(filters=UserPhoneOnlySchema(phone=user_data.phone))
    if old_user is None:
        await user_dao.add(
            UserAddWithCodeSchema(
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

    return {"message": "В"}


# set_tokens_to_response(response, user)
# check expiration
