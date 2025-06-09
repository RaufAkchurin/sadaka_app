from models.geo import Region
from sqladmin import ModelView


class RegionAdmin(ModelView, model=Region):
    icon = "fa-solid fa-map"
    name = "Регион"
    name_plural = "Регионы"

    form_excluded_columns = [
        "created_at",
        "updated_at",
        "funds",
    ]
