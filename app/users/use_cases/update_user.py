from fastapi import UploadFile

from app.s3_storage.use_cases.s3_upload import UploadFileUseCase
from app.users.dao import UsersDAO
from app.users.models import User
from app.users.schemas import UserUpdateResponseSchema, EmailModel, UserUpdateDataSchema


class UpdateUserUseCase:
    def __init__(self, users_dao: UsersDAO):
        self.users_dao = users_dao

    async def execute(self,
                      user: User,
                      update_data: UserUpdateDataSchema,
                      picture: UploadFile,
                      ) -> UserUpdateResponseSchema:
        use_case = UploadFileUseCase()
        s3_path = await use_case.execute(file=picture)

        await self.users_dao.update(filters=EmailModel(email=user.email),
                                       values=UserUpdateResponseSchema(
                                           name=update_data.name,
                                           picture=s3_path,
                                           city_id=update_data.city_id,
                                           email=update_data.email,
                                       ))

        updated_user = await self.users_dao.find_one_or_none_by_id(data_id=user.id)
        return UserUpdateResponseSchema(
                                name=updated_user.name,
                                picture=updated_user.picture,
                                city_id=updated_user.city_id,
                                email=updated_user.email,
                            )
