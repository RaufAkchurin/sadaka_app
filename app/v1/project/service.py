from sqlalchemy.ext.asyncio.session import AsyncSession

from app.v1.project.schemas import ProjectDetailAPISchema
from app.v1.users.dao import ProjectDAO


class ProjectDetailService:
    def __init__(self, session: AsyncSession):
        self.dao = ProjectDAO(session=session)

    async def get_project_detail_by_id(self, project_id: int) -> ProjectDetailAPISchema | None:
        result = await self.dao.get_fund_detail(data_id=project_id)
        if result is None:
            return None

        project, total_income, unique_sponsors = result
        collected_percentage = int((total_income / project.goal) * 100) if project.goal > 0 else 0

        return ProjectDetailAPISchema.model_validate(
            {
                "id": project.id,
                "status": project.status,
                "pictures_list": project.pictures_list,
                "fund": project.fund,
                "active_stage_number": project.active_stage_number,
                "name": project.name,
                "goal": project.goal,
                "total_income": total_income,
                "unique_sponsors": unique_sponsors,
                "collected_percentage": collected_percentage,
                "region": project.region,
                "description": project.description or "Описание отсутствует",
                "stages": project.stages,
                "documents": project.documents,
            }
        )
