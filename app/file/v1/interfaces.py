from typing import Protocol

from fastapi import UploadFile

from app.file.v1.models import File
from app.s3_storage.v1.schemas import S3UploadedFileSchema


class S3DeleteUseCaseProtocol(Protocol):
    async def __call__(self, file: File) -> None:
        ...


class S3UploadUseCaseProtocol(Protocol):
    async def __call__(self, file: UploadFile) -> S3UploadedFileSchema:
        ...
