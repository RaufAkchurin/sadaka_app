from fastapi import UploadFile
from pydantic.v1 import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.client.interfaces import S3ClientUseCaseProtocol
from app.dao.base import BaseDAO
from app.file.schemas import UploadedFileDataSchema
from app.file.use_cases.create_file import FileCreateWithContentUseCaseImpl
from app.file.use_cases.delete_file import FileDeleteWithContentUseCaseImpl
from app.s3_storage.use_cases.s3_upload import S3UploadUseCaseImpl
from app.users.dao import FileDAO, UserDAO
from app.users.models import User
from app.users.schemas import EmailModel, UserLogoUpdateSchema


class UserLogoUpdateUseCaseImpl:
    def __init__(self, session: AsyncSession, s3_client: S3ClientUseCaseProtocol) -> None:
        self.session: AsyncSession = session

        self.users_dao: BaseDAO = UserDAO(session=session)
        self.file_dao: BaseDAO = FileDAO(session=session)

        self.uploader = S3UploadUseCaseImpl(s3_client=s3_client)
        self.creator = FileCreateWithContentUseCaseImpl(session=self.session, uploader=self.uploader)
        self.deleter = FileDeleteWithContentUseCaseImpl(session=self.session, s3_client=s3_client)

    async def __call__(self, user: User, picture: UploadFile) -> UploadedFileDataSchema:
        mew_file_instance_data = await self.creator(picture=picture)

        if mew_file_instance_data.id and user.picture is not None:
            await self.deleter(user.picture.id)

        await self.users_dao.update(
            filters=EmailModel(email=EmailStr(user.email)),
            values=UserLogoUpdateSchema(picture_id=mew_file_instance_data.id),
        )
        return mew_file_instance_data
