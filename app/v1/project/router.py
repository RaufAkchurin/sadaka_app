from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ProjectNotFoundException
from app.models.referral import Referral
from app.models.user import User
from app.v1.api_utils.pagination import Pagination, PaginationParams, PaginationResponseSchema
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.project.enums import AbstractStatusEnum
from app.v1.project.schemas import ProjectDetailAPISchema, ProjectForListAPISchema
from app.v1.project.use_cases.list import ProjectListUseCase
from app.v1.referrals.router import ReferralKeyResponseSchema
from app.v1.users.dao import ProjectDAO, ReferralDAO, UserDAO

v1_projects_router = APIRouter()


@v1_projects_router.get("/all/{status_of_project}", response_model=PaginationResponseSchema[ProjectForListAPISchema])
async def get_projects_list(
    status_of_project: AbstractStatusEnum,
    fund_id: int = Query(default=None, alias="fund_id"),
    pagination: PaginationParams = Depends(),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> PaginationResponseSchema[ProjectForListAPISchema]:
    project_list_use_case = ProjectListUseCase()
    projects = await project_list_use_case(status_of_project, fund_id, session)
    return await Pagination.execute(projects, pagination.page, pagination.limit)


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


@v1_projects_router.get("/detail/{project_id}", response_model=ProjectDetailAPISchema)
async def get_project_detail_by_id(
    project_id: int,
    user_data: User = Depends(get_current_user),
    referral_checker: Referral | None = Depends(check_referral),
    session: AsyncSession = Depends(get_session_with_commit),
) -> ProjectDetailAPISchema:
    project = await ProjectDAO(session=session).find_one_or_none_by_id(data_id=project_id)

    if project is not None:
        return ProjectDetailAPISchema.model_validate(project)

    else:
        raise ProjectNotFoundException
