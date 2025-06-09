from admin.views.base.multiple_preview import MultipleFilesPreviewAdmin
from admin.views.base.picture_preview import AdminPicturePreview, BaseAdminView
from models.fund import Fund
from models.geo import City, Country, Region
from models.payment import Payment
from models.project import Project, Stage
from sqladmin import ModelView


class ProjectAdmin(MultipleFilesPreviewAdmin, model=Project):
    column_list = ["name", "status", "documents_preview", "pictures_preview"]
    icon = "fa-solid fa-diagram-project"
    name = "Проект"
    name_plural = "Проекты"

    form_excluded_columns = ["created_at", "updated_at", "payments", "documents", "stages", "pictures"]


############### ГЕОГРАФИЯ ############### # noqa E266


class CityAdmin(BaseAdminView, model=City):
    icon = "fa-solid fa-city"
    name = "Город"
    name_plural = "Города"


class RegionAdmin(ModelView, model=Region):
    icon = "fa-solid fa-map"
    name = "Регион"
    name_plural = "Регионы"

    # form_columns = [Region.name, Region.country, Region.citys, Region.funds]
    form_excluded_columns = ["created_at", "updated_at", "funds", "citys"]


class CountryAdmin(BaseAdminView, model=Country):
    icon = "fa-solid fa-globe"
    name = "Страна"
    name_plural = "Страны"


############### ФОНДЫ И ПРОЕКТЫ ############### # noqa E266


class FundAdminPicturePreview(AdminPicturePreview, model=Fund):
    icon = "fa-solid fa-hand-holding-heart"
    name = "Фонд"
    name_plural = "Фонды"


class StageAdmin(BaseAdminView, model=Stage):
    column_list = [Stage.id, Stage.name]
    icon = "fa-solid fa-layer-group"
    name = "Этап"
    name_plural = "Этапы"


############### ПЛАТЕЖИ ############### # noqa E266


class PaymentAdmin(BaseAdminView, model=Payment):
    column_list = [Payment.id]
    icon = "fa-solid fa-credit-card"
    name = "Платёж"
    name_plural = "Платежи"
