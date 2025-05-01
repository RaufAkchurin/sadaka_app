from sqlalchemy.ext.asyncio import AsyncSession

from app.client.interfaces import S3ClientUseCaseProtocol
from app.file.models import File
from app.s3_storage.interfaces import S3DeleteUseCaseProtocol
from app.s3_storage.use_cases.s3_delete import S3DeleteUseCase
from app.users.dao import FileDAO
from app.users.schemas import IdModel


class FileDeleteWithContentUseCase:
    def __init__(self, session: AsyncSession, s3_client: S3ClientUseCaseProtocol):
        self.session = session
        self.file_dao = FileDAO(session=session)
        self.s3_client = s3_client
        self.s3_deleter: S3DeleteUseCaseProtocol = S3DeleteUseCase(s3_client)

    async def __call__(self, file_id: int) -> None:
        file_instance: File = await self.file_dao.find_one_or_none_by_id(file_id)
        await self.file_dao.delete(filters=IdModel(id=file_id))
        await self.s3_deleter(file_instance.get_fullname)
