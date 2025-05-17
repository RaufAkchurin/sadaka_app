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

ДУМАТЬ
-сборы активные
-сборы завершенные
-отчёты
"""
from pydantic import BaseModel, ConfigDict

from app.v1.project.schemas import FileBaseSchema


class FundDetailAPISchema(BaseModel):
    id: int
    name: str
    region_name: str
    total_collected: int
    projects_count: int
    description: str
    hot_line: str
    address: str
    documents: list[FileBaseSchema]

    model_config = ConfigDict(from_attributes=True)
