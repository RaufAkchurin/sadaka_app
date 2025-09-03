import enum

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.v1.api_utils.pagination import PaginationParams
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.users.dao import PaymentDAO, ProjectDAO

v1_rating_router = APIRouter()


class RatingTypeEnum(str, enum.Enum):
    DONORS = "donors"
    REFERRALS = "referrals"
    REGIONS = "regions"
    PROJECTS = "projects"


class RatingResponseSchema(BaseModel):
    payments: int = 0
    autopayments: int = 0
    cities: int = 0
    projects: int = 0
    total_income: float = 0


@v1_rating_router.get("/{rating_type}")
async def get_projects_list(
    rating_type: RatingTypeEnum,
    pagination: PaginationParams = Depends(),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> RatingResponseSchema:
    payment_dao = PaymentDAO(session=session)
    payments = await payment_dao.count()
    total_income = await payment_dao.get_total_income()

    project_dao = ProjectDAO(session=session)
    projects = await project_dao.count()

    # project_list_use_case = ProjectListUseCase()
    # projects = await project_list_use_case(rating_type, fund_id, session)
    # return await Pagination.execute(projects, pagination.page, pagination.limit)
    return RatingResponseSchema(
        payments=payments, autopayments=0, cities=0, projects=projects, total_income=total_income
    )
