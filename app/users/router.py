from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth_dep import get_current_user, get_current_admin_user
from app.dependencies.dao_dep import get_session_with_commit
from app.users.dao import UsersDAO
from app.users.models import User
from app.users.schemas import SUserInfo, UserUpdateAPI
from app.users.use_cases.delete_user import DeleteUserUseCase
from app.users.use_cases.get_all_users import GetAllUsersUseCase
from app.users.use_cases.update_user import UpdateUserUseCase

router = APIRouter()

@router.get("/me/")
async def get_me(user_data: User = Depends(get_current_user)) -> SUserInfo:
    return SUserInfo.model_validate(user_data)


@router.put("/update/")
async def update_user(update_data: UserUpdateAPI,
                      session: AsyncSession = Depends(get_session_with_commit),
                      user: User = Depends(get_current_user)
                      ) -> UserUpdateAPI:

    dao = UsersDAO(session)
    use_case = UpdateUserUseCase(dao)
    return await use_case.execute(user=user, update_data=update_data)


@router.delete("/me/")
async def delete_user(session: AsyncSession = Depends(get_session_with_commit),
                      user: User = Depends(get_current_user)) -> dict:

    dao = UsersDAO(session)
    use_case = DeleteUserUseCase(dao)
    await use_case.execute(user=user)
    return {'message': 'Вы успешно удалили аккаунт!'}


#For admins only

@router.get("/all_users/")
async def get_all_users(session: AsyncSession = Depends(get_session_with_commit),
                        user_data: User = Depends(get_current_admin_user)
                        ) -> List[SUserInfo]:
    dao = UsersDAO(session)
    use_case = GetAllUsersUseCase(dao)
    return await use_case.execute()