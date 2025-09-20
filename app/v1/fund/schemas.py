"""
дитейл
-айди
-название
-название региона
----фонд собрал всего
----проектов всего
-о фонде
-горячая линия тел
-адрес
-документы
-сборы активные
-сборы завершенные

ДУМАТЬ
-отчёты
"""
from pydantic import BaseModel, ConfigDict

from app.v1.project.schemas import FileBaseSchema, ProjectForListAPISchema


class FundDetailAPISchema(BaseModel):
    id: int
    name: str
    description: str
    hot_line: str
    address: str

    region_name: str
    documents: list[FileBaseSchema]
    projects: list[ProjectForListAPISchema]

    total_income: float
    projects_count: int

    model_config = ConfigDict(from_attributes=True)
