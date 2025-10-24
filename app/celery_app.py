from __future__ import annotations

from celery import Celery
from celery.schedules import crontab
from loguru import logger

from app.settings import settings


def _crontab_from_string(expression: str) -> crontab:
    """Convert cron expression (m h dom mon dow) into Celery crontab."""
    try:
        minute, hour, day_of_month, month_of_year, day_of_week = expression.split()
    except ValueError as exc:  # pragma: no cover - configuration errors
        msg = f"Invalid cron expression provided: {expression}"
        raise ValueError(msg) from exc

    return crontab(
        minute=minute,
        hour=hour,
        day_of_month=day_of_month,
        month_of_year=month_of_year,
        day_of_week=day_of_week,
    )


celery_app = Celery(
    "sadaka_app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=False,
    task_default_queue="sadaka_app",
)

celery_app.autodiscover_tasks(["app.tasks"])

celery_app.conf.beat_schedule = {
    "send-daily-test-sms": {
        "task": "app.tasks.sms.send_daily_test_sms",
        "schedule": _crontab_from_string(settings.CELERY_TEST_SMS_CRONTAB),
    }
}

logger.info("Celery beat schedule loaded: {}", celery_app.conf.beat_schedule)
