from fastapi import HTTPException, UploadFile, status

from app.client.s3_client import S3Client
from app.exceptions import FileNotProvidedException
from app.settings import settings


class UploadFileUseCase:
    def __init__(self):
        self.s3_client: S3Client = S3Client(
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            endpoint_url=settings.S3_ENDPOINT_URL,
            bucket_name=settings.S3_BUCKET_NAME,
        )
        self.max_size_mb: int = 1
        self.supported_file_types = {"png": "png", "jpg": "jpg", "pdf": "pdf"}

    async def __call__(self, file: UploadFile) -> str | None:
        if not file:
            raise FileNotProvidedException()

        contents = await file.read()
        size = len(contents)

        # Проверка размера файла
        if not 0 < size <= self.max_size_mb * 1024 * 1024:  # 1 MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Supported file size is 0 - {self.max_size_mb} MB",
            )

        # Проверка типа файла
        file_type = file.filename.split(".")[-1]
        if file_type not in self.supported_file_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Неподдерживаемый тип файла: {file_type if file_type else "Unknown"}.'
                f' Поддерживаются только следующие типы {", ".join(self.supported_file_types)}',
            )

        # Генерация имени файла и загрузка в S3
        file_name = f'{file.filename.split(".")[0]}.{file_type}'
        await self.s3_client.upload_file(key=file_name, contents=contents)

        return settings.S3_FILE_BASE_URL + file_name
