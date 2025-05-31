from sqlalchemy.ext.asyncio import AsyncSession
from v1.city.schemas import CityListSchema
from v1.users.dao import CityDAO


class CityListUseCase:
    async def execute(self, session: AsyncSession) -> list[CityListSchema]:
        filtered_cities = await CityDAO(session=session).find_all()
        return [CityListSchema.model_validate(project) for project in filtered_cities]
