from typing import Protocol

from app.project.schemas import ProjectForListAPISchema


class ProjectForListUseCaseProtocol(Protocol):
    async def __call__(self) -> ProjectForListAPISchema:
        ...
