from app.models.user import User
from app.v1.project.schemas import FundIdFilter, ProjectForListAPISchema, StatusFilter
from app.v1.users.dao import ProjectDAO


class ProjectListUseCase:
    async def __call__(self, status_of_project, fund_id, session, user_data: User) -> list[ProjectForListAPISchema]:
        if status_of_project.value in ["active", "finished"]:
            if fund_id is None:
                filtered_projects = await ProjectDAO(session=session).find_all(
                    filters=StatusFilter(status=status_of_project)
                )
            else:
                filtered_projects = await ProjectDAO(session=session).find_all(
                    filters=FundIdFilter(status=status_of_project, fund_id=fund_id)
                )

        else:
            if fund_id is None:
                filtered_projects = await ProjectDAO(session=session).find_all()
            else:
                filtered_projects = await ProjectDAO(session=session).find_all(filters=FundIdFilter(fund_id=fund_id))

        # Фильтруем проекты по доступу пользователя к фондам
        if user_data.role.value != "superuser":
            filtered_projects = [p for p in filtered_projects if p.fund_id in user_data.funds_access_ids]

        return [ProjectForListAPISchema.model_validate(project) for project in filtered_projects]
