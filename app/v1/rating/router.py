import enum

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.v1.api_utils.pagination import Pagination, PaginationParams, PaginationResponseSchema
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.users.dao import PaymentDAO, ProjectDAO, UserDAO

v1_rating_router = APIRouter()


class RatingTypeEnum(str, enum.Enum):
    DONORS = "donors"
    REFERRALS = "referrals"
    REGIONS = "regions"
    PROJECTS = "projects"


class UserModelTotalIncomeSchema(BaseModel):
    name: str
    total_income: float = 0

    model_config = ConfigDict(from_attributes=True)


class RatingTotalInfoResponseSchema(BaseModel):
    payments: int = 0
    autopayments: int = 0
    cities: int = 0
    projects: int = 0
    total_income: float = 0


@v1_rating_router.get("/total_info")
async def get_total_info(
    pagination: PaginationParams = Depends(),
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
        autopayments=0,
        cities=cities_count,
        projects=projects,
        total_income=total_income,
    )


@v1_rating_router.get("/donors")
async def get_projects_list(
    pagination: PaginationParams = Depends(),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> PaginationResponseSchema[UserModelTotalIncomeSchema]:
    user_dao = UserDAO(session=session)
    users_ordered_by_payments = await user_dao.get_users_ordered_by_payments()
    serialized_users = [UserModelTotalIncomeSchema.model_validate(c) for c in users_ordered_by_payments]

    return await Pagination.execute(serialized_users, pagination.page, pagination.limit)
