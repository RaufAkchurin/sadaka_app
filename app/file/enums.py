import enum


class FileTypeEnum(enum.Enum):
    DOCUMENT = "DOCUMENT"
    REPORT = "REPORT"
    PICTURE = "PICTURE"


class MimeEnum(enum.Enum):
    PDF = "PDF"
    PNG = "PNG"
    JPEG = "JPEG"
