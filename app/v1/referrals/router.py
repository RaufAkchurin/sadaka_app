from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.referral import ReferralTypeEnum
from app.models.user import User
from app.v1.api_utils.db_pagination import DbPagination, DbPaginationResponseSchema
from app.v1.api_utils.pagination import PaginationParams
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.referrals.dao import ReferralDAO
from app.v1.referrals.schemas import ReferralAddSchema, ReferralDonationsSchema
from app.v1.referrals.utils import generate_referral_link
from app.v1.utils_core.id_validators import fund_id_validator, project_id_validator

v1_referral_router = APIRouter()


@v1_referral_router.get("/generate_link")
async def get_referral_link(
    ref_type: ReferralTypeEnum,
    fund_id: int = Query(default=None, alias="fund_id"),
    project_id: int = Query(default=None, alias="project_id"),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
):
    if fund_id is not None:
        await fund_id_validator(fund_id, session)
    if project_id is not None:
        await project_id_validator(project_id, session)

    referral_dao = ReferralDAO(session=session)

    referral = await referral_dao.add(
        values=ReferralAddSchema(
            type=ref_type,
            sharer_id=user_data.id,
            fund_id=fund_id,
            project_id=project_id,
        )
    )

    return await generate_referral_link(referral=referral) + f"?ref={referral.key}"


# ) -> PaginationResponseSchema[ReferralDonationsSchema]:


@v1_referral_router.get("/my_referral_list")
async def get_referrals_info(
    pagination: PaginationParams = Depends(),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> DbPaginationResponseSchema[ReferralDonationsSchema]:
    referral_dao = ReferralDAO(session=session)
    referrals = await referral_dao.get_referral_list(user_id=user_data.id, limit=pagination.limit)
    ser_referrals = [ReferralDonationsSchema.model_validate(r) for r in referrals]
    return await DbPagination.execute(ser_referrals, pagination.page, pagination.limit)
