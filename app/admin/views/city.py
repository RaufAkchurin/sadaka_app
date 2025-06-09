from admin.views.base_classes.image_as_file_singular_preview import BaseAdminView
from models.geo import City


class CityAdmin(BaseAdminView, model=City):
    icon = "fa-solid fa-city"
    name = "Город"
    name_plural = "Города"
