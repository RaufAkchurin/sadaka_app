from app.project.interfaces import ProjectListUseCaseProtocol
from app.project.models import Project


class ProjectListUseCaseImpl:
    def __init__(self, project: Project):
        self.project = project

    async def __call__(self, file_name: str) -> None:
        if file_name == "None":
            raise FileNameNotProvidedException
        await self.s3_client.delete_file(object_name=file_name)