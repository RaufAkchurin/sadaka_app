from typing import List

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.client.v1.interfaces import S3ClientUseCaseProtocol
from app.dependencies.v1.auth_dep import get_current_admin_user, get_current_user
from app.dependencies.v1.dao_dep import get_session_with_commit
from app.dependencies.v1.s3 import get_s3_client
from app.file.v1.schemas import UploadedFileDataSchema
from app.users.v1.dao import UserDAO
from app.users.v1.models import User
from app.users.v1.schemas import SUserInfo, UserDataUpdateSchema
from app.users.v1.use_cases.delete_user import DeleteUserUseCase
from app.users.v1.use_cases.get_all_users import GetAllUsersUseCase
from app.users.v1.use_cases.update_data import UserDataUpdateUseCase
from app.users.v1.use_cases.update_logo import UserLogoUpdateUseCaseImpl

v1_users_router = APIRouter()


@v1_users_router.get("/me")
async def get_me(user_data: User = Depends(get_current_user)) -> SUserInfo:
    return SUserInfo.model_validate(user_data)


@v1_users_router.put("/update_logo")
async def update_user_logo(
    picture: UploadFile,
    session: AsyncSession = Depends(get_session_with_commit),
    user: User = Depends(get_current_user),
    s3_client: S3ClientUseCaseProtocol = Depends(get_s3_client),
) -> UploadedFileDataSchema:
    use_case = UserLogoUpdateUseCaseImpl(session=session, s3_client=s3_client)
    updated_logo_url = await use_case(user=user, picture=picture)

    return updated_logo_url


@v1_users_router.put("/update_data")
async def update_user_data(
    update_data: UserDataUpdateSchema,
    session: AsyncSession = Depends(get_session_with_commit),
    user: User = Depends(get_current_user),
) -> UserDataUpdateSchema:
    use_case = UserDataUpdateUseCase(session=session)
    validated_data = await use_case(user=user, update_data=update_data)

    return validated_data


@v1_users_router.delete("/me")
async def delete_user(
    session: AsyncSession = Depends(get_session_with_commit),
    user: User = Depends(get_current_user),
) -> dict:
    dao = UserDAO(session)
    use_case = DeleteUserUseCase(dao)
    await use_case(user=user)

    return {"message": "Вы успешно удалили аккаунт!"}


# For admins only
@v1_users_router.get("/all_users")
async def get_all_users(
    session: AsyncSession = Depends(get_session_with_commit),
    user_data: User = Depends(get_current_admin_user),
) -> List[SUserInfo]:
    dao = UserDAO(session)
    use_case = GetAllUsersUseCase(dao)
    users = await use_case()

    return users
