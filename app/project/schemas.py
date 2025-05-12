from pydantic import BaseModel, ConfigDict

from app.project.enums import AbstractStatusEnum

"""
СПИСОК СБОРОВ
# id
# название сбора
# -необходимая сумма
# название фонда (ДОБАВИТЬ)
# этапы (нам нужен последний актуальный по идее только)
                    # платежи
# -собрали
# - количество спонсоров уникальных
# - процент закрытия от этапа
# - кнопка помочь
                    # этап АКТУАЛЬНЫЙ
#
# В БУДУЩЕМ---------------------------------
        Платежи
-собрали через тебя
        # ЛАЙКИ
# -Лайк от тебя на сбор стоит или нет
        # КОММЕНТЫ
# -количество коментов
#№№№ СОЦИАЛЬНЫЕ СЕТИ
# -вацап количество
# -телега количество
# -вк количество
"""

"""
СБОРЫ ДЕТАЛЬНО
"""


class StatusFilter(BaseModel):
    status: AbstractStatusEnum


class FileUrlSchema(BaseModel):
    url: str


class RegionShortSchema(BaseModel):
    name: str
    picture: FileUrlSchema


class FundShortSchema(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class StagesShortSchema(BaseModel):
    number: int
    name: str
    status: AbstractStatusEnum
    model_config = ConfigDict(from_attributes=True)


class StagesPaymentsSchema(StagesShortSchema):
    ...


class StagesReportSchema(StagesPaymentsSchema):
    ...


class ProjectPaymentsInfoSchema(BaseModel):
    total_collected: int
    unique_sponsors: int
    collected_percentage: int = 0


class ProjectListAPISchema(BaseModel):
    id: int
    status: AbstractStatusEnum
    name: str
    goal: int
    fund: FundShortSchema
    payments_total: ProjectPaymentsInfoSchema
    active_stage: StagesShortSchema | None = None

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailsAPISchema(ProjectListAPISchema):
    region_picture_url: str | None = None
    region_name: str | None = None
    description: str | None = "Описание отсутствует"
    stages: list[StagesShortSchema]
