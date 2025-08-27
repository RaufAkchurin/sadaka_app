from sqladmin import ModelView

from app.admin.views.auth_permissions import FundAdminAccess
from app.models.comment import Comment


class CommentAdmin(FundAdminAccess, ModelView, model=Comment):
    icon = "fa-solid fa-message"
    name = "Коммент"
    name_plural = "Комменты"
    can_create = True
    can_edit = True
    can_delete = True

    column_searchable_list = [Comment.project_id, Comment.user_id]
    form_excluded_columns = ["created_at", "updated_at"]
