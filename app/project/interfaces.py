from typing import Protocol

from app.project.schemas import ProjectListAPISchema


class ProjectListUseCaseProtocol(Protocol):
    async def __call__(self ) -> list[ProjectListAPISchema]:
        ...
