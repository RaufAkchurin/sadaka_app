from sqlalchemy import select, or_
from starlette.requests import Request

from app.admin.views.auth import get_token_payload
from app.admin.views.auth_permissions import FundAdminAccess
from app.admin.views.base_classes.image_as_field_upload import FileModelPictureUploadField
from app.models.file import File
from app.models.project import Project
from app.models.fund import Fund


class FileAdmin(FileModelPictureUploadField, FundAdminAccess, model=File):
    # TODO у файла поля отображаются только заполненные все сотальные скрывать
    # TODO привязка напрмиер только к юзеру а все остальное ненужно видеть в таком случае

    icon = "fa-solid fa-file-alt"
    name = "Файл"
    name_plural = "Файлы"
    can_export = False
    form_excluded_columns = [
        "name",  # because it inserts automatic
        "size",  # because it inserts automatic
        "mime",  # because it inserts automatic
        "type",  # because it inserts automatic
        "url",  # because it inserts automatic
        "created_at",
        "updated_at",
    ]

    def scaffold_form(self, *args, **kwargs):
        """Форма редактирования файла"""
        form = super().scaffold_form(*args, **kwargs)
        return form

    def list_query(self, request: Request):
        """Фильтрует список файлов по доступу к фондам"""
        payload = get_token_payload(request)
        
        # superuser видит все файлы
        if payload.user_role == "superuser":
            return select(self.model)
        
        # fund_admin видит только файлы своих фондов
        return select(self.model).where(
            # Файлы фондов пользователя
            File.fund_document_id.in_(payload.funds_access_ids)
        )


