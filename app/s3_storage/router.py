from fastapi import APIRouter, Depends
from ..client.s3_client import S3Client
from fastapi import  HTTPException, UploadFile, status, Response
from ..dependencies.auth_dep import get_current_user
from ..exceptions import FileNotProvidedException, FileNameNotProvidedException, FileNotFoundS3Exception
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
    'png': 'png',
    'jpg': 'jpg',
    'pdf': 'pdf'
}

@router.post('/upload')
async def upload(file: UploadFile | None = None,
                user_data: User = Depends(get_current_user),
                 ):
    if not file:
        raise FileNotProvidedException

    contents = await file.read()
    size = len(contents)
    max_size_mb = 1

    if not 0 < size <= max_size_mb * 1024 * 1024:  # 1 MB = 1 * 1024 * 1024 bytes
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Supported file size is 0 - {max_size_mb} MB'
        )

    type = file.filename.split(".")[1]
    if type not in SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Неподдерживаемый тип файла: {type if type else "Unknown"}. Поддерживаются только следующие типы {", ".join(SUPPORTED_FILE_TYPES)}'
        )

    file_name = f'{file.filename.split(".")[0]}.{SUPPORTED_FILE_TYPES[type]}'
    await s3_client.upload_file(key=file_name, contents=contents)
    return {'file_name': file_name}


@router.get('/download')
async def download(file_name: str | None = None,
                   user_data: User = Depends(get_current_user)
                   ):
    if not file_name:
        raise FileNameNotProvidedException

    contents = await s3_client.get_file(object_name=file_name)
    if contents is None:
        raise FileNotFoundS3Exception

    return Response(
        content=contents,
        headers={
            'Content-Disposition': f'attachment;filename={file_name}',
            'Content-Type': 'application/octet-stream',
        }
    )

@router.delete('/delete')
async def delete(file_name: str | None = None,
                user_data: User = Depends(get_current_user)
                ) -> dict:
    if file_name == 'None':
        raise FileNameNotProvidedException

    await s3_client.delete_file(object_name=file_name)
    return {'message': 'Запрос на удаление файла отправлен.'}
