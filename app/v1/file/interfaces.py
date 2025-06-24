from typing import Protocol

from fastapi import UploadFile

from app.models.file import File
from app.v1.s3_storage.schemas import S3UploadedFileSchema


class S3DeleteUseCaseProtocol(Protocol):
    async def __call__(self, file: File) -> None:
        ...


class S3UploadUseCaseProtocol(Protocol):
    async def __call__(self, file: UploadFile) -> S3UploadedFileSchema:
        ...
