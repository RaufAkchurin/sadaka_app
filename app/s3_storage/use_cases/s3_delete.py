from app.client.v1.interfaces import S3ClientUseCaseProtocol
from app.exceptions import FileNameNotProvidedException


class S3DeleteUseCaseImpl:
    def __init__(self, s3_client: S3ClientUseCaseProtocol):
        self.s3_client = s3_client

    async def __call__(self, file_name: str) -> None:
        if file_name == "None":
            raise FileNameNotProvidedException
        await self.s3_client.delete_file(object_name=file_name)
