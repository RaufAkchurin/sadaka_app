from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth_dep import get_current_user, get_current_admin_user
from app.dependencies.dao_dep import get_session_with_commit
from app.users.dao import UsersDAO
from app.users.models import User
from app.users.schemas import SUserInfo, UserUpdateAPI, EmailModel, UserActiveModel

router = APIRouter()

@router.get("/me/")
async def get_me(user_data: User = Depends(get_current_user)) -> SUserInfo:
    return SUserInfo.model_validate(user_data)

@router.post("/update/")
async def update_user(user_data: UserUpdateAPI,
                      session: AsyncSession = Depends(get_session_with_commit),
                      user: User = Depends(get_current_user)
                      ) -> UserUpdateAPI:
    await UsersDAO(session).update(filters=EmailModel(email=user.email),
                                            values=UserUpdateAPI(
                                                name=user_data.name,
                                                picture=user_data.picture,
                                                city_id=user_data.city_id,
                                                email=user_data.email,
                                            ))

    updated_user = await UsersDAO(session).find_one_or_none_by_id(user.id)
    return UserUpdateAPI(
        name=updated_user.name,
        picture=updated_user.picture,
        city_id=updated_user.city_id,
        email=updated_user.email,
    )

@router.post("/delete/")
async def update_user(session: AsyncSession = Depends(get_session_with_commit),
                      user: User = Depends(get_current_user)) -> dict:
    await UsersDAO(session).update(filters=EmailModel(email=user.email), values=UserActiveModel(is_active=False,))
    return {'message': 'Вы успешно удалили аккаунт!'}


#For admins only

@router.get("/all_users/")
async def get_all_users(session: AsyncSession = Depends(get_session_with_commit),
                        user_data: User = Depends(get_current_admin_user)
                        ) -> List[SUserInfo]:
    return await UsersDAO(session).find_all()