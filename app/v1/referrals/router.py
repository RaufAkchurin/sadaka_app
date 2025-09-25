import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict, Field, computed_field
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.referral import Referral, ReferralTypeEnum
from app.models.user import User
from app.settings import settings
from app.v1.api_utils.pagination import Pagination, PaginationParams, PaginationResponseSchema
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.referrals.dao import ReferralDAO
from app.v1.utils_core.id_validators import fund_id_validator, project_id_validator

v1_referral_router = APIRouter()


async def generate_referral_link(referral: Referral):
    url = ""

    if referral.type == ReferralTypeEnum.FUND:
        url = f"{settings.get_base_url}app/v1/funds/detail/{referral.fund_id}"

    elif referral.type == ReferralTypeEnum.PROJECT:
        url = f"{settings.get_base_url}app/v1/projects/detail/{referral.project_id}"

    elif referral.type == ReferralTypeEnum.JOIN:
        url = "ADD URL TO DOWNLOAD APP IN BACKEND PLEASE"

    return url


class ReferralKeyResponseSchema(BaseModel):
    key: str
    model_config = ConfigDict(from_attributes=True)


class ReferralAddSchema(BaseModel):
    type: ReferralTypeEnum
    sharer_id: int

    created_at: datetime.datetime | None = datetime.datetime.now()
    fund_id: int | None = None
    project_id: int | None = None


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


# PaginationResponseSchema
@v1_referral_router.get("/referral_list")
async def get_referrals_info(
    pagination: PaginationParams = Depends(),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> PaginationResponseSchema[ReferralDonationsSchema]:
    referral_dao = ReferralDAO(session=session)

    referrals: list[Referral] = await referral_dao.get_referral_list(user_id=user_data.id)

    ser_referrals = [ReferralDonationsSchema.model_validate(r) for r in referrals]

    return await Pagination.execute(ser_referrals, pagination.page, pagination.limit)
