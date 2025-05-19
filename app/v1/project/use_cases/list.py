from app.v1.project.schemas import FundIdFilter, ProjectForListAPISchema, StatusFilter
from app.v1.users.dao import ProjectDAO


class ProjectListUseCase:
    async def __call__(self, status_of_project, fund_id, page, limit, session) -> list[ProjectForListAPISchema]:
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

        filtered_projects = await pagination(filtered_projects, page, limit)

        return [ProjectForListAPISchema.model_validate(project) for project in filtered_projects]


async def pagination(queryset: list, page: int, limit: int):
    offset = (page - 1) * limit
    paginated_queryset = queryset[offset : offset + limit]

    return paginated_queryset
