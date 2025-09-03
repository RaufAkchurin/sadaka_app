from sqladmin import ModelView

from app.admin.views.auth_permissions import FundAdminAccess
from app.models.referral import Referral


class ReferralAdmin(FundAdminAccess, ModelView, model=Referral):
    icon = "fa-solid fa-link"
    name = "Реферрал"
    name_plural = "Реферралы"
    can_create = True
    can_edit = True
    can_delete = True

    # column_searchable_list = [Comment.project_id, Comment.user_id]
    form_excluded_columns = ["created_at", "updated_at"]
