from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth_dep import get_current_user
from app.dependencies.dao_dep import get_session_with_commit
from app.project.enums import AbstractStatusEnum
from app.project.schemas import ProjectListAPISchema, StatusFilter
from app.users.dao import ProjectDAO
from app.users.models import User

projects_router = APIRouter()

"""
Тест кейсы
-создать проект и чтобы у него были все Зконченные стадии проверять сколько в респонсе
-есть и законченные и активные
-есть только активные ???
"""


@projects_router.get("/{status_of_project}", response_model=list[ProjectListAPISchema])
async def get_me(
    status_of_project: AbstractStatusEnum,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> list[ProjectListAPISchema]:
    projects = await ProjectDAO(session=session).find_all(filters=StatusFilter(status=status_of_project))

    serialized_projects = [ProjectListAPISchema.model_validate(p) for p in projects]
    return serialized_projects


@projects_router.get("/detail/{project_id}")
async def get_detail():
    ...
