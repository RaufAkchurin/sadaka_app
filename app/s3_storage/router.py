from fastapi import APIRouter, Depends

from .use_cases.s3_delete import S3DeleteUseCase
from .use_cases.s3_download import S3DownloadFileUseCase
from .use_cases.s3_upload import UploadFileUseCase
from ..client.s3_client import S3Client
from fastapi import  HTTPException, UploadFile, status, Response
from ..dependencies.auth_dep import get_current_user
from ..exceptions import FileNotProvidedException, FileNameNotProvidedException, FileNotFoundS3Exception
from ..settings import settings
from ..users.models import User

router = APIRouter()

@router.post('/upload')
async def upload(file: UploadFile | None = None,
                user_data: User = Depends(get_current_user),
                 ):
    use_case = UploadFileUseCase()
    file_name = await use_case.execute(file=file)
    return {"file_name": file_name}


@router.get('/download')
async def download(file_name: str | None = None,
                   user_data: User = Depends(get_current_user)
                   ):
    use_case = S3DownloadFileUseCase()
    contents = await use_case.execute(file_name)

    return Response(
        content=contents,
        headers={
            'Content-Disposition': f'attachment;filename={file_name}',
            'Content-Type': 'application/octet-stream',
        }
    )

@router.delete('/delete')
async def delete(file_name: str,
                 user_data: User = Depends(get_current_user)) -> dict:
    use_case = S3DeleteUseCase()
    await use_case.execute(file_name)
    return {'message': 'Запрос на удаление файла отправлен.'}
