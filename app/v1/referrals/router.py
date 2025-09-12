from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.referral import ReferralTypeEnum
from app.models.user import User
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.users.dao import ReferralDAO

v1_referral_router = APIRouter()


class ReferralKeyResponseSchema(BaseModel):
    key: str
    model_config = ConfigDict(from_attributes=True)


class ReferralAddSchema(BaseModel):
    type: ReferralTypeEnum
    sharer_id: int

    fund_id: int | None = None
    project_id: int | None = None


@v1_referral_router.post("/generate_code")
async def get_referral_code(
    ref_type: ReferralTypeEnum,
    fund_id: int = Query(default=None, alias="fund_id"),
    project_id: int = Query(default=None, alias="project_id"),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> ReferralKeyResponseSchema | None:
    referral_dao = ReferralDAO(session=session)

    referral = await referral_dao.add(
        values=ReferralAddSchema(
            type=ref_type,
            sharer_id=user_data.id,
            fund_id=fund_id,
            project_id=project_id,
        )
    )
    return ReferralKeyResponseSchema(key=referral.key)
