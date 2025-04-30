from fastapi import UploadFile
from pydantic.v1 import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.file.schemas import UploadedFileDataSchema
from app.file.use_cases.create_file import CreateFileWithContentUseCase
from app.file.use_cases.delete_file import DeleteFileWithContentUseCase
from app.s3_storage.use_cases.s3_upload import UploadAnyFileToS3UseCase
from app.users.dao import FileDAO, UserDAO
from app.users.models import User
from app.users.schemas import EmailModel, UserLogoUpdateSchema


class UserLogoUpdateUseCase:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.users_dao = UserDAO(session=session)
        self.file_dao = FileDAO(session=session)
        uploader = UploadAnyFileToS3UseCase()
        self.creator = CreateFileWithContentUseCase(session=self.session, uploader=uploader)
        self.deleter = DeleteFileWithContentUseCase(session=self.session)

    async def __call__(self, user: User, picture: UploadFile) -> UploadedFileDataSchema:
        mew_file_instance_data = await self.creator(picture=picture)

        if mew_file_instance_data.id and user.picture is not None:
            await self.deleter(user.picture.id)

        await self.users_dao.update(
            filters=EmailModel(email=EmailStr(user.email)),
            values=UserLogoUpdateSchema(picture_id=mew_file_instance_data.id),
        )
        return mew_file_instance_data
