import math

from fastapi import Query
from pydantic import BaseModel, conint

from app.v1.project.schemas import FundIdFilter, ProjectForListAPISchema, StatusFilter
from app.v1.users.dao import ProjectDAO


class ProjectListUseCase:
    async def __call__(self, status_of_project, fund_id, session) -> list[ProjectForListAPISchema]:
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

        return [ProjectForListAPISchema.model_validate(project) for project in filtered_projects]


# TODO add test for paginator func
class PaginationParams(BaseModel):
    page: conint(gt=0) = Query(1, description="Page number")
    limit: conint(gt=0) = Query(2, description="Number of items per page")


class PaginationResponseStateSchema(BaseModel):
    page: int
    size: int
    total_pages: int
    total_items: int


class PaginatorResponseSchema(BaseModel):
    items: list
    state: PaginationResponseStateSchema


class Paginator:
    @staticmethod
    async def pagination(queryset: list, page: int, limit: int):
        offset = (page - 1) * limit
        paginated_queryset = queryset[offset : offset + limit]

        return PaginatorResponseSchema(
            items=paginated_queryset,
            state=PaginationResponseStateSchema(
                page=page,
                size=limit,
                total_pages=math.ceil(len(queryset) / limit),
                total_items=len(queryset),
            ),
        )
