from fastapi import UploadFile

# from app.file.use_cases.upload_user_avatar import CreateFileInstanceWithUserAvatarUseCase
# from app.tests.conftest import session
from app.users.dao import UserDAO
from app.users.models import User
from app.users.schemas import EmailModel, UserLogoUpdateSchema


class UserLogoUpdateUseCase:
    def __init__(self, users_dao: UserDAO):
        self.users_dao = users_dao

    async def __call__(self, user: User, picture: UploadFile) -> UserLogoUpdateSchema:
        ...
        # TODO нужен готовый инстанс ФАЙЛА и лишь его мы тут привязываем
        # file_crate_use_case = CreateFileInstanceWithUserAvatarUseCase(session=session)

        # await self.users_dao.update(
        #     filters=EmailModel(email=user.email),
        #     values=UserLogoUpdateSchema(url=s3_path),
        # )
        #
        # updated_user = await self.users_dao.find_one_or_none_by_id(data_id=user.id)
        # updated_picture_url = UserLogoUpdateSchema(picture_url=updated_user.picture_url)
        # return updated_picture_url
