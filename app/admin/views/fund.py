from app.admin.views.auth_permissions import SuperAdminPerm
from app.admin.views.base_classes.image_as_file_singular_preview import AdminPicturePreview
from app.models.fund import Fund


class FundAdmin(SuperAdminPerm, AdminPicturePreview, model=Fund):
    icon = "fa-solid fa-hand-holding-heart"
    name = "Фонд"
    name_plural = "Фонды"
    can_export = False

    form_excluded_columns = [
        "projects",
        "created_at",
        "updated_at",
    ]  # because sqladmin error for relations
