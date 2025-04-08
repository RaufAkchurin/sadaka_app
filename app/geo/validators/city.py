from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.dao_dep import get_session_with_commit
from app.users.dao import CityDAO


async def city_id_validator(city_id: int, session: AsyncSession):
    city_dao = CityDAO(session=session)
    city = await city_dao.find_one_or_none_by_id(data_id=city_id)
    if city is None:
        raise HTTPException(status_code=400, detail="Нет города с данным city_id ")