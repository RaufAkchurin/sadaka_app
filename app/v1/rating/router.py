from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.v1.api_utils.pagination import Pagination, PaginationParams, PaginationResponseSchema
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.rating.schemas import (
    ProjectRatingSchema,
    RatingTotalInfoResponseSchema,
    RegionModelTotalIncomeSchema,
    UserModelTotalIncomeSchema,
)
from app.v1.referrals.dao import ReferralDAO
from app.v1.users.dao import PaymentDAO, ProjectDAO, RegionDAO, UserDAO

v1_rating_router = APIRouter()


@v1_rating_router.get("/total_info")
async def get_total_info(
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> RatingTotalInfoResponseSchema:
    payment_dao = PaymentDAO(session=session)

    payments_count = await payment_dao.count()
    total_income = await payment_dao.count_payments_total_income()
    cities_count = await payment_dao.count_payment_cities()

    project_dao = ProjectDAO(session=session)
    projects = await project_dao.count()

    return RatingTotalInfoResponseSchema(
        payments=payments_count,
        autopayments=0,  # TODO after adding payment system change it
        cities=cities_count,
        projects=projects,
        total_income=total_income,
    )


@v1_rating_router.get("/donors")
async def get_donors_rating(
    pagination: PaginationParams = Depends(),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> PaginationResponseSchema[UserModelTotalIncomeSchema]:
    user_dao = UserDAO(session=session)
    users_ordered_by_payments = await user_dao.get_users_ordered_by_payments()
    serialized_users = [UserModelTotalIncomeSchema.model_validate(c) for c in users_ordered_by_payments]

    return await Pagination.execute(serialized_users, pagination.page, pagination.limit)


@v1_rating_router.get("/regions_all")
async def get_regions_rating(
    project_id: int | None = None,
    pagination: PaginationParams = Depends(),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> PaginationResponseSchema[RegionModelTotalIncomeSchema]:
    region_dao = RegionDAO(session=session)
    regions_ordered_by_payments = await region_dao.get_regions_ordered_by_payments()
    serialized_regions = [RegionModelTotalIncomeSchema.model_validate(c) for c in regions_ordered_by_payments]

    return await Pagination.execute(serialized_regions, pagination.page, pagination.limit)


@v1_rating_router.get("/regions/{project_id}")
async def get_regions_rating_by_project_id(
    project_id: int,
    pagination: PaginationParams = Depends(),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> PaginationResponseSchema[RegionModelTotalIncomeSchema]:
    region_dao = RegionDAO(session=session)
    regions_ordered_by_payments = await region_dao.get_regions_ordered_by_payments_for_project(project_id=project_id)
    serialized_regions = [RegionModelTotalIncomeSchema.model_validate(c) for c in regions_ordered_by_payments]

    return await Pagination.execute(serialized_regions, pagination.page, pagination.limit)


@v1_rating_router.get("/projects")
async def get_projects_rating(
    pagination: PaginationParams = Depends(),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> PaginationResponseSchema[ProjectRatingSchema]:
    project_dao = ProjectDAO(session=session)

    projects_ordered_by_payments = await project_dao.get_projects_ordered_by_payments()
    serialized_regions = [ProjectRatingSchema.model_validate(c) for c in projects_ordered_by_payments]

    return await Pagination.execute(serialized_regions, pagination.page, pagination.limit)


@v1_rating_router.get("/referrals")
async def get_referred_payments_rating(
    pagination: PaginationParams = Depends(),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
):
    referral_dao = ReferralDAO(session=session)
    projects_ordered_by_payments = await referral_dao.get_users_sorted_by_ref_income()
    serialized_users_by_ref_payments = [
        UserModelTotalIncomeSchema.model_validate(u) for u in projects_ordered_by_payments
    ]
    return await Pagination.execute(serialized_users_by_ref_payments, pagination.page, pagination.limit)
