import filetype
from fastapi import APIRouter
from ..client.s3_client import S3Client
from uuid import uuid4
from fastapi import  HTTPException, UploadFile, status

router = APIRouter()

s3_client = S3Client(
    access_key="691a26fb9f03473e95db9fdacc9af1d9",
    secret_key="226e51b0eb864925908ac11fc7746504",
    endpoint_url="https://s3.ru-7.storage.selcloud.ru",
    bucket_name="sadaka",
)

KB = 1024
MB = 1024 * KB

SUPPORTED_FILE_TYPES = {
    'image/png': 'png',
    'image/jpeg': 'jpg',
    'application/pdf': 'pdf'
}


@router.post('/upload')
async def upload(file: UploadFile | None = None):
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No file found!!'
        )

    contents = await file.read()
    size = len(contents)

    if not 0 < size <= 1 * 1024 * 1024:  # 1 MB = 1 * 1024 * 1024 bytes
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Supported file size is 0 - 1 MB'
        )

    kind = filetype.guess(contents)
    if kind is None or kind.mime not in SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Unsupported file type: {kind.mime if kind else "Unknown"}. Supported types are {", ".join(SUPPORTED_FILE_TYPES)}'
        )

    file_name = f'{uuid4()}.{kind.extension}'  # используем расширение, которое определено filetype
    await s3_client.upload_file(key=file_name, contents=contents)

    return {'file_name': file_name}


@router.get('/download')
async def download(file_name: str | None = None):
    if not file_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No file name provided'
        )

    contents = await s3_download(key=file_name)
    return Response(
        content=contents,
        headers={
            'Content-Disposition': f'attachment;filename={file_name}',
            'Content-Type': 'application/octet-stream',
        }
    )
