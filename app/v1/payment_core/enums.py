from enum import Enum


class RecurringPaymentStatusEnum(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"


class RecurringPaymentIntervalEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
