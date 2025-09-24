from app.v1.project.service import ProjectService


class ProjectListUseCase:
    async def __call__(
        self,
        status_of_project,
        fund_id,
        session,
        page: int = 1,
        size: int = 5,
    ) -> dict:
        service = ProjectService(session=session)
        return await service.get_projects_list(
            status_of_project.value if status_of_project is not None else None,
            fund_id,
            page,
            size,
        )
