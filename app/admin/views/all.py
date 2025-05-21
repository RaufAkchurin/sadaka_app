from admin.views.base import BaseAdminView, CreateWithPictureAdmin
from models.file import File
from models.fund import Fund
from models.geo import City, Country, Region
from models.payments import Payment
from models.project import Project, Stage

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


class ProjectAdmin(BaseAdminView, model=Project):
    icon = "fa-solid fa-diagram-project"
    name = "Проект"
    name_plural = "Проекты"


class StageAdmin(BaseAdminView, model=Stage):
    column_list = [Stage.id, Stage.name]
    icon = "fa-solid fa-layer-group"
    name = "Этап"
    name_plural = "Этапы"


class FileAdmin(CreateWithPictureAdmin, model=File):
    # TODO у файла поля отображаются только заполненные все сотальные скрывать
    # TODO тк привязка напрмиер только к юзеру а все остальное ненужно видеть в таком случае

    icon = "fa-solid fa-file-alt"
    name = "Файл"
    name_plural = "Файлы"


############### ПЛАТЕЖИ ############### # noqa E266


class PaymentAdmin(BaseAdminView, model=Payment):
    column_list = [Payment.id]
    icon = "fa-solid fa-credit-card"
    name = "Платёж"
    name_plural = "Платежи"
