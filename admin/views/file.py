from admin.views.base_classes.image_as_field_upload import FileModelPictureUploadField
from app.models.file import File


class FileAdmin(FileModelPictureUploadField, model=File):
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
