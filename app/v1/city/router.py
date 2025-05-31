from fastapi import APIRouter, Depends
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from v1.api_utils.pagination import Pagination, PaginationParams, PaginationResponseSchema
from v1.city.schemas import CityListSchema
from v1.city.use_cases.list import CityListUseCase
from v1.dependencies.auth_dep import get_current_user
from v1.dependencies.dao_dep import get_session_with_commit

v1_city_router = APIRouter()


@v1_city_router.get("/all", response_model=PaginationResponseSchema[CityListSchema])
async def get_cities_list(
    pagination: PaginationParams = Depends(),
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> PaginationResponseSchema[CityListSchema]:
    city_list_use_case = CityListUseCase()
    cities = await city_list_use_case.execute(session)
    return await Pagination.execute(cities, pagination.page, pagination.limit)
