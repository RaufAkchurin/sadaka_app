from app.client.s3_client import S3Client
from app.exceptions import FileNameNotProvidedException
from app.settings import settings


class S3DeleteUseCase:

    def __init__(self):
        self.s3_client: S3Client = S3Client(
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            endpoint_url=settings.S3_ENDPOINT_URL,
            bucket_name=settings.S3_BUCKET_NAME,
        )

    async def __call__(self, file_name: str) -> None:
        if file_name == "None":
            raise FileNameNotProvidedException
        await self.s3_client.delete_file(object_name=file_name)
