from app.client.s3_client import S3Client
from app.exceptions import (FileNameNotProvidedException,
                            FileNotFoundS3Exception)
from app.settings import settings


class S3DownloadFileUseCase:
    def __init__(self):
        self.s3_client: S3Client  = S3Client(
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            endpoint_url=settings.S3_ENDPOINT_URL,
            bucket_name=settings.S3_BUCKET_NAME,
        )
    async def execute(self, file_name: str) -> bytes:
        if not file_name:
            raise FileNameNotProvidedException
        contents = await self.s3_client.get_file(object_name=file_name)
        if contents is None:
            raise FileNotFoundS3Exception
        return contents