from admin.views.base import BaseAdminView, CreateWithPictureAdmin
from app.documents.models import Document
from app.fund import City, Country, Region
from app.fund.models import Fund
from app.payments.models import Payment
from app.project.models import Project, Stage
from app.users.models import Role

############### ПОЛЬЗОВАТЕЛИ ###############  # noqa E266


class RoleAdmin(BaseAdminView, model=Role):
    icon = "fa-solid fa-user-tag"
    name = "Роль"
    name_plural = "Роли"


############### ГЕОГРАФИЯ ############### # noqa E266


class CityAdmin(BaseAdminView, model=City):
    icon = "fa-solid fa-city"
    name = "Город"
    name_plural = "Города"


class RegionAdmin(CreateWithPictureAdmin, model=Region):
    icon = "fa-solid fa-map"
    name = "Регион"
    name_plural = "Регионы"


class CountryAdmin(BaseAdminView, model=Country):
    icon = "fa-solid fa-globe"
    name = "Страна"
    name_plural = "Страны"


############### ФОНДЫ И ПРОЕКТЫ ############### # noqa E266


class FundAdmin(CreateWithPictureAdmin, model=Fund):
    icon = "fa-solid fa-hand-holding-heart"
    name = "Фонд"
    name_plural = "Фонды"


class ProjectAdmin(CreateWithPictureAdmin, model=Project):
    icon = "fa-solid fa-diagram-project"
    name = "Проект"
    name_plural = "Проекты"


class StageAdmin(BaseAdminView, model=Stage):
    column_list = [Stage.id, Stage.name]
    icon = "fa-solid fa-layer-group"
    name = "Этап"
    name_plural = "Этапы"


class DocumentAdmin(BaseAdminView, model=Document):
    icon = "fa-solid fa-file-alt"
    name = "Документ"
    name_plural = "Документы"


############### ПЛАТЕЖИ ############### # noqa E266


class PaymentAdmin(BaseAdminView, model=Payment):
    column_list = [Payment.id]
    icon = "fa-solid fa-credit-card"
    name = "Платёж"
    name_plural = "Платежи"
