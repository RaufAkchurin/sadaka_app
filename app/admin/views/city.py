from admin.views.base_classes.image_as_file_singular_preview import BaseAdminView
from models.city import City
from starlette.requests import Request
from v1.dependencies.auth_dep import get_current_user


class CityAdmin(BaseAdminView, model=City):
    icon = "fa-solid fa-city"
    name = "Город"
    name_plural = "Города"

    def is_accessible(self, request: Request) -> bool:
        """Override this method to add permission checks.
        SQLAdmin does not make any assumptions about the authentication system
        used in your application, so it is up to you to implement it.
        By default, it will allow access for everyone.
        """

        user = await get_current_user(token=token, session=session)
        return False
