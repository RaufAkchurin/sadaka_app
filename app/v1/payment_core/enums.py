from enum import Enum


class RecurringPaymentStatusEnum(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"  # created but not yet active
    PAUSED = "paused"
    PAST_DUE = "past_due"
    FAILED = "failed"
    CANCELED = "canceled"


class RecurringPaymentIntervalEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class PaymentMethodEnum(str, Enum):
    CARD = "card"
    SBP = "sbp"
