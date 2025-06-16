from admin.views.auth import get_token_payload
from admin.views.auth_permissions import FundAdminAccess
from admin.views.base_classes.image_as_file_singular_preview import BaseAdminView
from models.project import Project
from models.stage import Stage
from sqlalchemy import select
from starlette.requests import Request


class StageAdmin(BaseAdminView, FundAdminAccess, model=Stage):
    column_list = [Stage.id, Stage.name]
    icon = "fa-solid fa-layer-group"
    name = "Этап"
    name_plural = "Этапы"
    can_export = False

    form_excluded_columns = [
        "payments",  # because sqladmin error for relations
        "created_at",
        "updated_at",
    ]

    column_searchable_list = [Stage.project_id]

    def list_query(self, request: Request):
        payload = get_token_payload(request)
        stmt = select(self.model).join(Project, Stage.project_id == Project.id)

        # фильтруем по фондам
        if payload.user_role.value != "superuser":
            stmt = stmt.where(Project.fund_id.in_(payload.funds_access_ids))

        return stmt
