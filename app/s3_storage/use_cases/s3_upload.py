from fastapi import HTTPException, UploadFile, status

from app.client.s3_client import S3Client
from app.exceptions import FileNotProvidedException
from app.file.enums import FileTypeEnum, MimeEnum
from app.s3_storage.schemas import S3UploadedFileSchema
from app.settings import settings


class UploadAnyFileToS3UseCase:
    def __init__(self):
        self.s3_client: S3Client = S3Client(
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            endpoint_url=settings.S3_ENDPOINT_URL,
            bucket_name=settings.S3_BUCKET_NAME,
        )
        self.max_size_mb: int = 2

        # Маппинг расширений -> (MimeEnum, FileTypeEnum)
        self.supported_file_types = {
            "png": (MimeEnum.PNG, FileTypeEnum.PICTURE),
            "jpg": (MimeEnum.JPEG, FileTypeEnum.PICTURE),
            "jpeg": (MimeEnum.JPEG, FileTypeEnum.PICTURE),
            "pdf": (MimeEnum.PDF, FileTypeEnum.DOCUMENT),
        }

    async def __call__(self, file: UploadFile) -> S3UploadedFileSchema:
        if not file:
            raise FileNotProvidedException()

        contents = await file.read()

        # Проверка размера файла
        if not 0 < len(contents) <= self.max_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Supported file size is 0 - {self.max_size_mb} MB",
            )

        # Извлекаем расширение
        extension = file.filename.split(".")[-1].lower()

        if extension not in self.supported_file_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f'Неподдерживаемый тип файла: {extension if extension else "Unknown"}. '
                    f'Поддерживаются только следующие типы {", ".join(self.supported_file_types.keys())}'
                ),
            )

        mime, file_type = self.supported_file_types[extension]

        await self.s3_client.upload_file(key=file.filename, contents=contents)

        validated_data = S3UploadedFileSchema(
            name=f'{file.filename.rsplit(".", 1)[0]}',
            size=len(contents),
            url=settings.S3_FILE_BASE_URL + file.filename,
            type=file_type,
            mime=mime,
        )

        return validated_data
