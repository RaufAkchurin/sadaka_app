from markupsafe import Markup
from sqladmin import ModelView


class BaseAdminView(ModelView):
    form_excluded_columns = ["created_at", "updated_at"]
    column_list = ["id", "name"]


class AdminPicturePreview(BaseAdminView):
    column_list = ["id", "name", "picture_url"]
    form_excluded_columns = ["created_at", "updated_at", "upload"]

    column_details_list = ["picture_url"]

    @staticmethod
    def _picture_preview(model, name):
        url = getattr(model, "picture_url")
        if url:
            return Markup(f'<img src="{url}" width="50" height="50" style="object-fit:cover;border-radius:40px;" />')
        return "—"

    column_formatters = {
        "picture_url": _picture_preview,
    }

    column_formatters_list = column_formatters
    column_formatters_detail = column_formatters

    column_labels = {
        "picture_url": "Превью",
    }

    # # FILE ACTIONS
    #
    # def __init__(self):
    #     super().__init__()
    #     self.s3_client = get_s3_client()
    #
    # async def scaffold_form(self, form_rules=None):
    #     form_class = await super().scaffold_form()
    #     form_class.picture_file = FileField("Загрузить файл")
    #     return form_class
    #
    # async def insert_model(self, request: Request, data: dict):
    #     form = await request.form()
    #     file: UploadFile = form.get("picture_file", None)
    #
    #     if file and file.filename:
    #         use_case = S3UploadUseCaseImpl(s3_client=self.s3_client)
    #         s3_file = await use_case(file=file)
    #         data["url"] = s3_file.url
    #
    #     return await super().insert_model(request, data)
