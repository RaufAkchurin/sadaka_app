from admin.views.base_classes.image_as_file_singular_preview import AdminPicturePreview
from fastapi import Request, UploadFile
from wtforms import FileField

from app.v1.dependencies.dao_dep import get_session_without_commit
from app.v1.dependencies.s3 import get_s3_client
from app.v1.file.use_cases.create_file import FileCreateWithContentUseCaseImpl
from app.v1.s3_storage.use_cases.s3_upload import S3UploadUseCaseImpl
from app.v1.users.dao import FileDAO


class FileModelPictureUploadField(AdminPicturePreview):
    def __init__(self):
        super().__init__()
        self.s3_client = get_s3_client()

    async def scaffold_form(self, form_rules=None):
        form_class = await super().scaffold_form()
        form_class.upload = FileField()  # we always have it, but without file it size == 0
        return form_class

    async def insert_model(self, request: Request, data: dict):
        file: UploadFile = data.pop("upload")

        # Получаем сессию для работы с БД
        session_gen = get_session_without_commit()
        session = await session_gen.__anext__()

        if file and file.filename:
            use_case = S3UploadUseCaseImpl(s3_client=self.s3_client)

            new_use_case = FileCreateWithContentUseCaseImpl(uploader=use_case, session=session)
            new_file_data = await new_use_case(picture=file)

            file_dao = FileDAO(session)
            user_instance = await file_dao.find_one_or_none_by_id(data_id=new_file_data.id)

            await session.commit()
            return user_instance

    async def update_model(self, request, pk, data):
        file: UploadFile = data.pop("upload")

        if file.size != 0:
            use_case = S3UploadUseCaseImpl(s3_client=self.s3_client)
            s3_file = await use_case(file=file)
            data["url"] = s3_file.url

        return await super().update_model(request, pk, data)
