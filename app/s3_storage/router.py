from fastapi import APIRouter, Depends, Response, UploadFile

from app.dependencies.auth_dep import get_current_user
from app.s3_storage.use_cases.s3_delete import S3DeleteUseCase
from app.s3_storage.use_cases.s3_download import S3DownloadFileUseCase
from app.s3_storage.use_cases.s3_upload import UploadFileUseCase
from app.users.models import User

s3_router = APIRouter()


@s3_router.post('/upload')
async def upload(file: UploadFile | None = None,
                 user_data: User = Depends(get_current_user)) -> dict:
    use_case = UploadFileUseCase()
    file_name = await use_case.execute(file=file)
    return {"file_name": file_name}


@s3_router.get('/{file_name}')
async def download(file_name: str,
                   user_data: User = Depends(get_current_user)) -> Response:
    use_case = S3DownloadFileUseCase()
    contents = await use_case.execute(file_name)

    return Response(
        content=contents,
        headers={
            'Content-Disposition': f'attachment;filename={file_name}',
            'Content-Type': 'application/octet-stream',
        }
    )

@s3_router.delete('/{file_name}')
async def delete(file_name: str,
                 user_data: User = Depends(get_current_user)) -> dict:
    use_case = S3DeleteUseCase()
    await use_case.execute(file_name)
    return {'message': 'Запрос на удаление файла отправлен.'}
