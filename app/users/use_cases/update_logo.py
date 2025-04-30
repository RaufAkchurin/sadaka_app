from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.file.schemas import UploadedFileDataSchema
from app.file.use_cases.upload_user_avatar import CreateFileWithPictureUseCase
from app.s3_storage.use_cases.s3_delete import S3DeleteUseCase
from app.users.dao import FileDAO, UserDAO
from app.users.models import User
from app.users.schemas import EmailModel, UserLogoUpdateSchema


class UserLogoUpdateUseCase:
    def __init__(self, session: AsyncSession):
        self.users_dao = UserDAO(session=session)
        self.file_dao = FileDAO(session=session)
        self.session = session

    async def __call__(self, user: User, picture: UploadFile) -> UploadedFileDataSchema:
        file_crate_with_avatar_use_case = CreateFileWithPictureUseCase(session=self.session)
        mew_file_instance_data = await file_crate_with_avatar_use_case(picture=picture)

        if mew_file_instance_data.id and user.picture is not None:
            # deleting from S3
            # TODO add usecase who will delete FIle instance and from S3 in it
            s3_delete_use_case = S3DeleteUseCase()
            await s3_delete_use_case(file_name=user.picture.name + "." + str(user.picture.mime).lower())

        await self.users_dao.update(
            filters=EmailModel(email=user.email),
            values=UserLogoUpdateSchema(picture_id=mew_file_instance_data.id),
        )
        return mew_file_instance_data
