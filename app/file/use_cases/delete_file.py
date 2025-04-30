from sqlalchemy.ext.asyncio import AsyncSession

from app.file.models import File
from app.s3_storage.use_cases.s3_delete import S3DeleteUseCase
from app.users.dao import FileDAO
from app.users.schemas import IdModel


class DeleteFileWithContentUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.file_dao = FileDAO(session=session)
        self.s3_deleter = S3DeleteUseCase()

    async def __call__(self, file_id: int) -> None:
        file_instance: File = await self.file_dao.find_one_or_none_by_id(file_id)
        await self.file_dao.delete(filters=IdModel(id=file_id))
        await self.s3_deleter(file_instance.get_fullname)

        # return UploadedFileDataSchema(
        #     id=file_instance.id,
        #     name=s3_uploaded_file_data.name,
        #     size=s3_uploaded_file_data.size,
        #     url=s3_uploaded_file_data.url,
        #     type=s3_uploaded_file_data.type,
        #     mime=s3_uploaded_file_data.mime,
        # )
