from typing import Optional

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.referral import Referral
from app.models.user import User
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.referrals.dao import ReferralDAO
from app.v1.referrals.router import ReferralKeyResponseSchema
from app.v1.users.dao import UserDAO


async def check_referral(
    ref: Optional[str] = Query(default=None, alias="ref"),
    session: AsyncSession = Depends(get_session_with_commit),
    user_data: User = Depends(get_current_user),
):
    if ref is None:
        return None

    referral_dao = ReferralDAO(session=session)
    user_dao = UserDAO(session=session)

    referral: Referral = await referral_dao.find_one_or_none(filters=ReferralKeyResponseSchema(key=ref))
    if referral is not None:
        user = await user_dao.find_one_or_none_by_id(data_id=user_data.id)
        referral.referees.append(user)

        await session.commit()
        await session.refresh(referral)
        await session.refresh(user)
