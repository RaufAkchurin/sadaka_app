from typing import Protocol

from fastapi import UploadFile

from app.s3_storage.schemas import S3UploadedFileSchema


class AbstractUploadFileToS3UseCase(Protocol):
    async def __call__(self, file: UploadFile) -> S3UploadedFileSchema:
        ...
