from admin.views.auth_permissions import FundAdminAccess
from sqladmin import ModelView

from app.models.payment import Payment


class PaymentAdmin(FundAdminAccess, ModelView, model=Payment):
    icon = "fa-solid fa-credit-card"
    name = "Платёж"
    name_plural = "Платежи"
    can_create = False
    can_edit = False
    can_delete = False

    column_exclude_list = ["id", "user", "captured_at", "updated_at", "project_id", "stage_id", "user_id"]
    column_searchable_list = [Payment.project_id]
