from admin.views.base.multiple_preview import DocumentsPreviewAdmin
from models.project import Project


class ProjectAdmin(DocumentsPreviewAdmin, model=Project):
    icon = "fa-solid fa-diagram-project"
    name = "Проект"
    name_plural = "Проекты"
