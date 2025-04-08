from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.dao import CityDAO


class CityIdValidationUseCase:
    def __init__(self,
                 session: AsyncSession):
        self.city_dao = CityDAO(session)

    async def execute(self, city_id: int):
        city = await self.city_dao.find_one_or_none_by_id(data_id=city_id)
        if city is None:
            raise HTTPException(status_code=400, detail="Нет города с данным city_id ")