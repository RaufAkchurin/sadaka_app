from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.file.v1.interfaces import S3UploadUseCaseProtocol
from app.file.v1.schemas import UploadedFileDataSchema
from app.users.v1.dao import FileDAO


class FileCreateWithContentUseCaseImpl:
    def __init__(self, session: AsyncSession, uploader: S3UploadUseCaseProtocol):
        self.session = session
        self.uploader = uploader
        self.file_dao = FileDAO(session=session)

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
