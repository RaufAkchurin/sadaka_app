from fastapi import UploadFile
from app.s3_storage.use_cases.s3_upload import UploadFileUseCase
from app.users.dao import UsersDAO
from app.users.models import User
from app.users.schemas import EmailModel, UserLogoUpdateSchema


class UserLogoUpdateUseCase:
    def __init__(self, users_dao: UsersDAO):
        self.users_dao = users_dao

    async def execute(self,
                      user: User,
                      picture: UploadFile) -> UserLogoUpdateSchema:
        use_case = UploadFileUseCase()
        s3_path = await use_case.execute(file=picture)

        await self.users_dao.update(filters=EmailModel(email=user.email),
                                    values=UserLogoUpdateSchema(
                                        picture=s3_path
                                        )
                                    )

        updated_user = await self.users_dao.find_one_or_none_by_id(data_id=user.id)
        updated_picture_url = UserLogoUpdateSchema(picture=updated_user.picture)
        return updated_picture_url
