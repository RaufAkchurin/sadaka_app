from pydantic import AnyHttpUrl, BaseModel

from app.file.enums import FileTypeEnum, MimeEnum


class S3UploadedFileSchema(BaseModel):
    name: str
    size: int
    url: AnyHttpUrl
    type: FileTypeEnum
    mime: MimeEnum
