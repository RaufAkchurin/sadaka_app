from fastapi import Request, UploadFile
from sqladmin import ModelView
from wtforms import FileField

from app.s3_storage.use_cases.s3_upload import UploadFileUseCase
from app.users.models import User


class UserAdmin(ModelView, model=User):
    name_plural = "Пользователи"
    name = "Пользователь"

    icon = "fa-solid fa-user"
    column_list = [
        User.id,
        User.name,
        User.email,
        User.language,
        User.city_id,
        User.role_id,
        User.picture_url,
        # "avatar_preview"
    ]
    column_searchable_list = [User.name, User.email]
    column_sortable_list = [User.id, User.name, User.email]
    column_labels = {
        User.id: "ID",
        User.name: "Имя",
        User.email: "Email",
        User.language: "Язык",
        User.picture_url: "URL аватарки",
        # "avatar_preview": "Аватар",
    }

    form_columns = [
        User.name,
        User.email,
        User.language,
        User.city_id,
        User.role_id,
        # "avatar_preview",
    ]

    async def scaffold_form(self, form_rules=None):
        form_class = await super().scaffold_form()
        form_class.picture_file = FileField("Загрузить аватар")
        return form_class

    async def insert_model(
        self,
        request: Request,
        data: dict,
    ):
        form = await request.form()
        file: UploadFile = form.get("picture_file")

        if file and file.filename:
            use_case = UploadFileUseCase()
            s3_path = await use_case(file=file)
            data["picture_url"] = s3_path

        return await super().insert_model(request, data)

    #

    # async def update_model(self, request: Request, pk: str, data: dict) -> Any:
    #     return await super().update_model(request=request, pk=pk, data=data)

    # async def update_model(self,
    #                        request: Request,
    #                        data: dict,
    #                        model: User,
    #                        session: AsyncSession = Depends(get_session_with_commit),
    #                        ):
    #     form = await request.form()
    #     file: UploadFile = form.get("picture_url")
    #
    #     if file and file.filename:
    #         dao = UsersDAO(session)
    #         use_case = UserLogoUpdateUseCase(users_dao=dao)
    #         url = await use_case(user=model, picture=file)
    #         data["picture_url"] = url
    #
    #     return await super().update_model(request=request, pk= data=data)

    # def avatar_preview(self: User, value):
    #     if self.picture_url:
    #         return f'<img src="{self.picture_url}" width="50" height="50" style="object-fit:cover;border-radius:50%;" />'
    #     return "—"

    # column_formatters = {
    #     "avatar_preview": avatar_preview
    # }

    # column_formatters_detail = column_formatters
    # column_formatters_list = column_formatters
    # column_formatters_args = {
    #     "avatar_preview": {"is_safe": True}
    # }
