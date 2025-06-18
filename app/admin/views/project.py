from admin.views.auth import get_token_payload
from admin.views.auth_permissions import FundAdminAccess
from admin.views.base_classes.image_as_file_multiple_preview import MultipleFilesPreviewAdmin
from models.project import Project
from sqlalchemy import false, select
from starlette.requests import Request


class ProjectAdmin(MultipleFilesPreviewAdmin, FundAdminAccess, model=Project):
    column_list = ["name", "status", "documents_preview", "pictures_preview"]
    icon = "fa-solid fa-diagram-project"
    name = "Проект"
    name_plural = "Проекты"
    can_export = False

    form_excluded_columns = [
        "payments",  # because sqladmin error for relations
        "stages",  # because sqladmin error for relations
        "created_at",
        "updated_at",
    ]
    column_searchable_list = [Project.fund_id]

    def list_query(self, request: Request):
        """
        The SQLAlchemy select expression used for the list page which can be customized.
        By default it will select all objects without any filters.
        """
        payload = get_token_payload(request)

        if not payload.funds_access_ids and payload.user_role.value != "superuser":
            # if list empty its work without error
            return select(self.model).where(false())

        if payload.user_role.value != "superuser":  # filtering by fund_ids_access
            return select(self.model).where(self.model.fund_id.in_(payload.funds_access_ids))

        return select(self.model)
