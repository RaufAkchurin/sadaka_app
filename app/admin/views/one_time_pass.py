from app.admin.views.auth_permissions import SuperAdminPerm
from app.admin.views.base_classes.image_as_file_singular_preview import BaseAdminView
from app.models.one_time_pass import OneTimePass


class OneTimePassAdmin(BaseAdminView, SuperAdminPerm, model=OneTimePass):
    icon = "fa-solid fa-key"
    name = "Пароль подтверждения"
    name_plural = "Пароли подтверждения"
    can_export = False

