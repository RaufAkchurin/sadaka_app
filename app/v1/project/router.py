from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.exceptions import ProjectNotFoundException
from app.models.referral import Referral
from app.models.user import User
from app.v1.api_utils.pagination import PaginationParams, PaginationResponseSchema
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.project.enums import ProjectStatusEnum
from app.v1.project.schemas import ProjectDetailAPISchema, ProjectForListAPISchema
from app.v1.project.service import ProjectService
from app.v1.project.use_cases.list import ProjectListUseCase
from app.v1.referrals.depends import check_referral

v1_projects_router = APIRouter()


@v1_projects_router.get(
    "/all/{status_of_project}",
    response_model=PaginationResponseSchema[ProjectForListAPISchema],
    status_code=status.HTTP_200_OK,
)
async def get_projects_list(
    status_of_project: ProjectStatusEnum,
    fund_id: int | None = Query(default=None, alias="fund_id"),
    pagination: PaginationParams = Depends(),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
):
    project_list_use_case = ProjectListUseCase()
    return await project_list_use_case(
        status_of_project=status_of_project,
        fund_id=fund_id,
        session=session,
        page=pagination.page,
        size=pagination.limit,
    )


@v1_projects_router.get("/detail/{project_id}", response_model=ProjectDetailAPISchema)
async def get_project_detail_by_id(
    project_id: int,
    user_data: User = Depends(get_current_user),
    referral_checker: Referral | None = Depends(check_referral),
    session: AsyncSession = Depends(get_session_with_commit),
) -> ProjectDetailAPISchema:
    service = ProjectService(session=session)
    project = await service.get_project_detail_by_id(project_id=project_id)

    if project is not None:
        return ProjectDetailAPISchema.model_validate(project)

    else:
        raise ProjectNotFoundException
