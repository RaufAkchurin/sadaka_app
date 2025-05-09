from pydantic import BaseModel, ConfigDict

from app.project.enums import AbstractStatusEnum

"""
СПИСОК СБОРОВ
# id
# название сбора
# -необходимая сумма
# название фонда (ДОБАВИТЬ)



                    # этап АКТУАЛЬНЫЙ
# -номер этапа


                    # платежи
# -собрали
# - количество спонсоров уникальных
# - процент закрытия от этапа
# -кнопка помочь
#
# в будущем
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


class StatusFilter(BaseModel):
    status: AbstractStatusEnum


class FundShortSchema(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class StagesShortSchema(BaseModel):
    number: int
    name: str
    status: AbstractStatusEnum
    model_config = ConfigDict(from_attributes=True)


class ProjectListAPISchema(BaseModel):
    id: int
    name: str
    status: AbstractStatusEnum
    goal: int
    fund: FundShortSchema
    stages: list[StagesShortSchema]

    model_config = ConfigDict(from_attributes=True)


class FileSchema(BaseModel):
    id: int
    name: str
    url: str
    type: str
    mime: str

    model_config = ConfigDict(from_attributes=True)


# class ProjectDetailAPISchema(BaseModel):
#     id: int
#     name: str
#     status: AbstractStatusEnum
#     description: Optional[str]
#
#     # funds: List[FundShortSchema] = []
#     documents: List[FileSchema] = []
#     pictures: List[FileSchema] = []
#     stages: List[StageSchema] = []
#
#     model_config = ConfigDict(from_attributes=True)
