from pydantic import BaseModel


class InstanceIdFilterSchema(BaseModel):
    user_id: int | None = None
    project_id: int | None = None
    stage_id: int | None = None
