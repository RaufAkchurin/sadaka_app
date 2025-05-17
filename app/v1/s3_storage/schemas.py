from pydantic import BaseModel

from app.v1.file.enums import FileTypeEnum, MimeEnum


class S3UploadedFileSchema(BaseModel):
    name: str
    size: int
    url: str
    type: FileTypeEnum
    mime: MimeEnum
