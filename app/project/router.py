from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth_dep import get_current_user
from app.dependencies.dao_dep import get_session_with_commit
from app.exceptions import ProjectNotFoundException
from app.project.enums import AbstractStatusEnum
from app.project.schemas import ProjectDetailAPISchema, ProjectForListAPISchema, StatusFilter
from app.project.use_cases.list_payment import ProjectForListUseCaseImpl
from app.users.dao import ProjectDAO
from app.users.models import User

projects_router = APIRouter()

"""
Тест кейсы
-создать проект и чтобы у него были все Зконченные стадии проверять сколько в респонсе
-есть и законченные и активные
-есть только активные ???
2 - осздать различные платежи и првоерять ответы
кейс - отсутствуют этапы вообще
"""


@projects_router.get("/all/{status_of_project}", response_model=list[ProjectForListAPISchema])
async def get_projects_list(
    status_of_project: AbstractStatusEnum,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> list[ProjectForListAPISchema]:
    filtered_projects = await ProjectDAO(session=session).find_all(filters=StatusFilter(status=status_of_project))

    serialized_projects = []
    for project in filtered_projects:
        use_case = ProjectForListUseCaseImpl()
        updated_project = use_case(project)
        serialized_projects.append(ProjectForListAPISchema.model_validate(updated_project))

    return serialized_projects


# TODO проверить несущ айди
# TODO В БД к проекту не привязываются картинки в отличие от документов
# TODO переделать pictures_list под КАРТИНКИ, а доки это для заглушки сделано
@projects_router.get("/detail/{project_id}", response_model=ProjectDetailAPISchema)
async def get_project_detail_by_id(
    project_id: int,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> ProjectDetailAPISchema:
    project = await ProjectDAO(session=session).find_one_or_none_by_id(data_id=project_id)

    if project is not None:
        use_case = ProjectForListUseCaseImpl()
        updated_project = use_case(project)
        return ProjectDetailAPISchema.model_validate(updated_project)

    else:
        raise ProjectNotFoundException
