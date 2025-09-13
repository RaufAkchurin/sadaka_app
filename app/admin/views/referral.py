from sqladmin import ModelView

from app.admin.views.auth_permissions import FundAdminAccess
from app.models.referral import Referral


class ReferralAdmin(FundAdminAccess, ModelView, model=Referral):
    icon = "fa-solid fa-link"
    name = "Реферрал"
    name_plural = "Реферралы"
