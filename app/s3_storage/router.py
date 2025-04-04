import filetype
from fastapi import APIRouter, Depends
from ..client.s3_client import S3Client
from uuid import uuid4
from fastapi import  HTTPException, UploadFile, status, Response

from ..dependencies.auth_dep import get_current_user
from ..exceptions import FileNotFoundException, FileNameNotProvidedException
from ..settings import settings
from ..users.models import User

router = APIRouter()

s3_client = S3Client(
    access_key=settings.S3_ACCESS_KEY,
    secret_key=settings.S3_SECRET_KEY,
    endpoint_url=settings.S3_ENDPOINT_URL,
    bucket_name=settings.S3_BUCKET_NAME,
)

KB = 1024
MB = 1024 * KB

SUPPORTED_FILE_TYPES = {
    'image/png': 'png',
    'image/jpeg': 'jpg',
    'application/pdf': 'pdf'
}

@router.post('/upload')
async def upload(file: UploadFile | None = None,
                # user_data: User = Depends(get_current_user)
                 ):
    if not file:
        raise FileNotFoundException

    contents = await file.read()
    size = len(contents)
    max_size_mb = 1

    if not 0 < size <= max_size_mb * 1024 * 1024:  # 1 MB = 1 * 1024 * 1024 bytes
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Supported file size is 0 - {max_size_mb} MB'
        )

    kind = filetype.guess(contents)
    if kind is None or kind.mime not in SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Неподдерживаемый тип файла: {kind.mime if kind else "Unknown"}. Поддерживаются только следующие типы {", ".join(SUPPORTED_FILE_TYPES)}'
        )

    file_name = f'{uuid4()}.{SUPPORTED_FILE_TYPES[kind.mime]}'
    await s3_client.upload_file(key=file_name, contents=contents)
    return {'file_name': file_name}


@router.get('/download')
async def download(file_name: str | None = None,
                   # user_data: User = Depends(get_current_user)
                   ) -> Response:
    if not file_name:
        raise FileNameNotProvidedException

    contents = await s3_client.get_file(object_name=file_name)
    return Response(
        content=contents,
        headers={
            'Content-Disposition': f'attachment;filename={file_name}',
            'Content-Type': 'application/octet-stream',
        }
    )

@router.delete('/delete')
async def delete(file_name: str | None = None,
                # user_data: User = Depends(get_current_user)
                ) -> dict:
    if not file_name:
        raise FileNameNotProvidedException

    await s3_client.delete_file(object_name=file_name)
    return {'message': 'Файл успешно удалён.'}
