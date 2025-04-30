from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.file.interfaces import AbstractUploadFileToS3UseCase
from app.file.schemas import UploadedFileDataSchema
from app.users.dao import FileDAO


class CreateFileWithContentUseCase:

    def __init__(self, session: AsyncSession, uploader: AbstractUploadFileToS3UseCase):
        self.session = session
        self.file_dao = FileDAO(session=session)
        self.uploader = uploader

    async def __call__(self, picture: UploadFile) -> UploadedFileDataSchema | None:
        try:
            s3_uploaded_file_data = await self.uploader(file=picture)
            file_instance = await self.file_dao.add(values=s3_uploaded_file_data)

            return UploadedFileDataSchema(
                id=file_instance.id,
                name=s3_uploaded_file_data.name,
                size=s3_uploaded_file_data.size,
                url=s3_uploaded_file_data.url,
                type=s3_uploaded_file_data.type,
                mime=s3_uploaded_file_data.mime,
            )
        except Exception as e:
            raise e
