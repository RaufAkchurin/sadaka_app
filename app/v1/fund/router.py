from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import FundNotFoundException, ForbiddenException
from app.models.user import User
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.fund.schemas import FundDetailAPISchema
from app.v1.users.dao import FundDAO

v1_funds_router = APIRouter()


@v1_funds_router.get("/detail/{fund_id}", response_model=FundDetailAPISchema)
async def get_fund_detail_by_id(
    fund_id: int,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_with_commit),
) -> FundDetailAPISchema:
    # Проверяем доступ пользователя к фонду
    if fund_id not in user_data.funds_access_ids and user_data.role.value != "superuser":
        raise ForbiddenException
    
    fund = await FundDAO(session=session).find_one_or_none_by_id(data_id=fund_id)

    if fund is not None:
        # Фильтруем проекты по доступу пользователя к фондам
        if user_data.role.value != "superuser":
            filtered_projects = [p for p in fund.projects if p.fund_id in user_data.funds_access_ids]
            # Создаем временный объект с отфильтрованными проектами
            fund.projects = filtered_projects
        
        return FundDetailAPISchema.model_validate(fund)

    else:
        raise FundNotFoundException
