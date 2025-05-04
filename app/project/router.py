from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth_dep import get_current_user
from app.dependencies.dao_dep import get_session_with_commit
from app.project.schemas import ProjectInfoSchema
from app.users.dao import ProjectDAO
from app.users.models import User

projects_router = APIRouter()


@projects_router.get("/")
async def get_me(
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> list[ProjectInfoSchema]:
    projects = await ProjectDAO(session=session).find_all()

    serialized_projects = [ProjectInfoSchema.model_validate(p) for p in projects]
    return serialized_projects
