from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, conint
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ProjectNotFoundException
from app.models.user import User
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.project.enums import AbstractStatusEnum
from app.v1.project.schemas import ProjectDetailAPISchema, ProjectForListAPISchema
from app.v1.project.use_cases.list import ProjectListUseCase
from app.v1.users.dao import ProjectDAO

v1_projects_router = APIRouter()


# TODO for tests add with status all
# TODO add test for paginator func
class PaginationParams(BaseModel):
    page: conint(gt=0) = Query(1, description="Page number")
    limit: conint(gt=0) = Query(25, description="Number of items per page")


@v1_projects_router.get("/all/{status_of_project}", response_model=list[ProjectForListAPISchema])
async def get_projects_list(
    status_of_project: AbstractStatusEnum,
    fund_id: int = Query(default=None, alias="fund_id"),
    pagination: PaginationParams = Depends(),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> list[ProjectForListAPISchema]:
    project_list_use_case = ProjectListUseCase()

    return await project_list_use_case(status_of_project, fund_id, pagination.page, pagination.limit, session)


@v1_projects_router.get("/detail/{project_id}", response_model=ProjectDetailAPISchema)
async def get_project_detail_by_id(
    project_id: int,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> ProjectDetailAPISchema:
    project = await ProjectDAO(session=session).find_one_or_none_by_id(data_id=project_id)

    if project is not None:
        return ProjectDetailAPISchema.model_validate(project)

    else:
        raise ProjectNotFoundException
