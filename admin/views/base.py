from fastapi import Request, UploadFile
from markupsafe import Markup
from sqladmin import ModelView
from wtforms import FileField

from app.s3_storage.use_cases.s3_upload import UploadFileUseCase


class BaseAdminView(ModelView):
    form_excluded_columns = ["created_at", "updated_at"]
    column_list = ["id", "name"]


class CreateWithPictureAdmin(BaseAdminView):
    column_list = ["id", "name", "picture_url"]
    form_excluded_columns = ["created_at", "updated_at", "url"]

    async def scaffold_form(self, form_rules=None):
        form_class = await super().scaffold_form()
        form_class.picture_file = FileField("Загрузить картинку")
        return form_class

    async def insert_model(self, request: Request, data: dict):
        form = await request.form()
        file: UploadFile = form.get("picture_file")

        if file and file.filename:
            use_case = UploadFileUseCase()
            s3_path = await use_case(file=file)
            data["url"] = s3_path

        return await super().insert_model(request, data)

    @staticmethod
    def _picture_preview(model, name):
        url = getattr(model, "url", None)
        if url:
            return Markup(f'<img src="{url}" width="100" height="100" style="object-fit:cover;border-radius:40px;" />')
        return "—"

    column_formatters = {
        "picture_url": _picture_preview,
    }

    column_formatters_list = column_formatters
    column_formatters_detail = column_formatters

    column_labels = {
        "picture_url": "Превью",
    }
