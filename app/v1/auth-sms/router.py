from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1.auth.router import v1_auth_router
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.users.dao import UserDAO
from app.v1.users.schemas import SUserAddSchema, UserPhoneSchema


@v1_auth_router.post("/sms/register/")
async def register_by_sms(
    user_data: UserPhoneSchema,
    session: AsyncSession = Depends(get_session_with_commit),
) -> dict:
    user_dao = UserDAO(session)
    user_data_dict = user_data.model_dump()
    await user_dao.add(values=SUserAddSchema(**user_data_dict, is_active=True))

    return {"message": "Вы успешно зарегистрированы!"}
