from sqladmin import ModelView

from app.admin.views.auth_permissions import FundAdminAccess
from app.models.payment import Payment


class PaymentAdmin(FundAdminAccess, ModelView, model=Payment):
    icon = "fa-solid fa-credit-card"
    name = "Платёж"
    name_plural = "Платежи"

    column_list = [
        Payment.id,
        Payment.amount,
        Payment.income_amount,
        Payment.status,
        Payment.project_id,
        Payment.created_at,
    ]

    column_searchable_list = [Payment.project_id]

    column_details_list = [
        Payment.id,
        Payment.user,
        Payment.project,
        Payment.stage,
        Payment.referral,
        Payment.amount,
        Payment.income_amount,
        Payment.test,
        Payment.status,
    ]
