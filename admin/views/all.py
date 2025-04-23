from sqladmin import ModelView

from app.documents.models import Document
from app.fund import City, Country, Region
from app.fund.models import Fund
from app.payments.models import Payment
from app.project.models import Project, Stage
from app.users.models import Role, User


class BaseView(ModelView):
    form_excluded_columns = [User.created_at, User.updated_at]


############### ПОЛЬЗОВАТЕЛИ ###############


class RoleAdmin(BaseView, model=Role):
    column_list = [Role.id, Role.name]
    icon = "fa-solid fa-user-tag"
    name = "Роль"
    name_plural = "Роли"


# class UserAdmin(BaseView, model=User):
#     column_list = [User.id, User.name]
#     icon = "fa-solid fa-user"
#     name = "Пользователь"
#     name_plural = "Пользователи"


############### ГЕОГРАФИЯ ###############


class CityAdmin(BaseView, model=City):
    column_list = [City.id, City.name]
    icon = "fa-solid fa-city"
    name = "Город"
    name_plural = "Города"


class RegionAdmin(BaseView, model=Region):
    column_list = [Region.id, Region.name]
    icon = "fa-solid fa-map"
    name = "Регион"
    name_plural = "Регионы"


class CountryAdmin(BaseView, model=Country):
    column_list = [Country.id, Country.name]
    icon = "fa-solid fa-globe"
    name = "Страна"
    name_plural = "Страны"


############### ФОНДЫ И ПРОЕКТЫ ###############


class FundAdmin(BaseView, model=Fund):
    column_list = [Fund.id, Fund.name]
    icon = "fa-solid fa-hand-holding-heart"
    name = "Фонд"
    name_plural = "Фонды"


class ProjectAdmin(BaseView, model=Project):
    column_list = [Project.id, Project.name]
    icon = "fa-solid fa-diagram-project"
    name = "Проект"
    name_plural = "Проекты"


class StageAdmin(BaseView, model=Stage):
    column_list = [Stage.id, Stage.name]
    icon = "fa-solid fa-layer-group"
    name = "Этап"
    name_plural = "Этапы"


class DocumentAdmin(BaseView, model=Document):
    column_list = [Document.id, Document.name]
    icon = "fa-solid fa-file-alt"
    name = "Документ"
    name_plural = "Документы"


############### ПЛАТЕЖИ ###############


class PaymentAdmin(BaseView, model=Payment):
    column_list = [Payment.id]
    icon = "fa-solid fa-credit-card"
    name = "Платёж"
    name_plural = "Платежи"
