from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ProjectNotFoundException
from app.models.user import User
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.project.enums import AbstractStatusEnum
from app.v1.project.schemas import ProjectDetailAPISchema, ProjectForListAPISchema, StatusFilter
from app.v1.users.dao import ProjectDAO

v1_projects_router = APIRouter()


@v1_projects_router.get("/all/{status_of_project}", response_model=list[ProjectForListAPISchema])
async def get_projects_list(
    status_of_project: AbstractStatusEnum,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> list[ProjectForListAPISchema]:
    filtered_projects = await ProjectDAO(session=session).find_all(filters=StatusFilter(status=status_of_project))

    serialized_projects = []
    for project in filtered_projects:
        serialized_projects.append(ProjectForListAPISchema.model_validate(project))

    return serialized_projects


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
