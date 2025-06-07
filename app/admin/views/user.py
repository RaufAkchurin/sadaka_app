from admin.views.base.picture_preview import AdminPicturePreview
from models.user import User


class UserAdminPicturePreview(AdminPicturePreview, model=User):
    name_plural = "Пользователи"
    name = "Пользователь"

    icon = "fa-solid fa-user"
    # column_list = [User.id, User.name, User.email, User.language, User.city_id]
    column_searchable_list = [User.name, User.email]
    column_sortable_list = [User.id, User.name, User.email]
    column_labels = {
        User.id: "ID",
        User.name: "Имя",
        User.email: "Email",
        User.language: "Язык",
    }
