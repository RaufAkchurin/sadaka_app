from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class DbPaginationResponseStateSchema(BaseModel):
    page: int
    per_page: int
    on_page: int
    has_more: bool


class DbPaginationResponseSchema(BaseModel, Generic[T]):
    items: list[T]
    state: DbPaginationResponseStateSchema


class DbPagination:
    @staticmethod
    async def execute(queryset: list[T], page: int, limit: int) -> DbPaginationResponseSchema[T]:
        len_queryset = len(queryset)
        has_more = len_queryset > limit
        on_page = len_queryset if len_queryset <= limit else limit  # тк в выборке может быть больше на один от лимита

        return DbPaginationResponseSchema[T](
            items=queryset[:limit],
            state=DbPaginationResponseStateSchema(
                page=page,
                per_page=limit,
                on_page=on_page,
                has_more=has_more,
            ),
        )
