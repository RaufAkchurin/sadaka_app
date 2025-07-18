from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.region import Region
from app.v1.client.interfaces import S3ClientUseCaseProtocol
from app.v1.dao.base import BaseDAO
from app.v1.file.schemas import UploadedFileDataSchema
from app.v1.file.use_cases.create_file import FileCreateWithContentUseCaseImpl
from app.v1.file.use_cases.delete_file import FileDeleteWithContentUseCaseImpl
from app.v1.s3_storage.use_cases.s3_upload import S3UploadUseCaseImpl
from app.v1.users.dao import FileDAO, RegionDAO
from app.v1.users.schemas import IdSchema, PictureIdSchema


class RegionPictureUpdateUseCaseImpl:
    def __init__(self, session: AsyncSession, s3_client: S3ClientUseCaseProtocol) -> None:
        self.session: AsyncSession = session

        self.regions_dao: RegionDAO = RegionDAO(session=session)
        self.file_dao: BaseDAO = FileDAO(session=session)

        self.uploader = S3UploadUseCaseImpl(s3_client=s3_client)
        self.creator = FileCreateWithContentUseCaseImpl(session=self.session, uploader=self.uploader)
        self.deleter = FileDeleteWithContentUseCaseImpl(session=self.session, s3_client=s3_client)

    async def __call__(self, region: Region, picture: UploadFile) -> UploadedFileDataSchema:
        mew_file_instance_data = await self.creator(picture=picture)

        await self.regions_dao.update(
            filters=IdSchema(id=region.id),
            values=PictureIdSchema(picture_id=mew_file_instance_data.id),
        )

        if mew_file_instance_data.id and region.picture is not None:
            await self.deleter(region.picture.id)

        return mew_file_instance_data
