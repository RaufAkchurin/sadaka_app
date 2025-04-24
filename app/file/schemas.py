from typing import Any, Optional

from pydantic import BaseModel, model_validator

from app.file.enums import FileTypeEnum


class FileCreate(BaseModel):
    # TODO CHECK IT BEFORE USING !!!!
    name: str
    file_type: FileTypeEnum
    size: int
    link: str

    project_id: Optional[int] = None
    fund_id: Optional[int] = None
    report_id: Optional[int] = None

    @model_validator(mode="before")
    def validate_related_ids(self, values: dict[str, Any]) -> dict[str, Any]:
        related_ids = [values.get("project_id"), values.get("fund_id"), values.get("report_id")]
        num_set = sum(bool(i) for i in related_ids)

        if num_set == 0:
            raise ValueError("Нужно указать хотя бы одну связанную сущность (project, fund, report).")
        if num_set > 1:
            raise ValueError("Можно указать только одну связанную сущность.")
        return values
