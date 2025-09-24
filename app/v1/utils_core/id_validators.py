from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1.users.dao import CityDAO, FundDAO, ProjectDAO, UserDAO


async def city_id_validator(city_id: int, session: AsyncSession):
    city_dao = CityDAO(session=session)
    city = await city_dao.find_one_or_none_by_id(data_id=city_id)
    if city is None:
        raise HTTPException(status_code=422, detail="Нет города с данным city_id.")


async def project_id_validator(project_id: int, session: AsyncSession):
    project_dao = ProjectDAO(session=session)
    city = await project_dao.find_one_or_none_by_id(data_id=project_id)
    if city is None:
        raise HTTPException(status_code=422, detail="Нет сущности с данным project_id.")


async def fund_id_validator(fund_id: int, session: AsyncSession):
    fund_dao = FundDAO(session=session)
    fund = await fund_dao.find_one_or_none_by_id(data_id=fund_id)
    if fund is None:
        raise HTTPException(status_code=422, detail="Нет сущности с данным fund_id.")


async def user_id_validator(user_id: int, session: AsyncSession):
    user_dao = UserDAO(session=session)
    user = await user_dao.find_one_or_none_by_id(data_id=user_id)
    if user is None:
        raise HTTPException(status_code=422, detail="Нет пользователя с данным user_id.")
