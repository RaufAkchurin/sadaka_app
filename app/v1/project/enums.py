import enum


class ProjectStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    FINISHED = "finished"
    ALL = "all"
