from __future__ import annotations

from celery import shared_task
from loguru import logger

from app.settings import settings
from app.v1.auth_sms.service_smsc import SMSC


@shared_task(name="app.tasks.sms.send_daily_test_sms")
def send_daily_test_sms() -> dict[str, str]:
    """Send a daily test SMS to confirm Celery setup works."""
    phone = settings.CELERY_TEST_SMS_PHONE
    message = settings.CELERY_TEST_SMS_MESSAGE

    if settings.MODE == "TEST":
        logger.debug("Skipping SMS send in TEST mode.")
        return {"status": "skipped", "reason": "test-mode"}

    normalized_phone = phone[1:] if phone.startswith("+") else phone

    smsc = SMSC()
    smsc.send_sms(normalized_phone, message, sender=settings.CELERY_TEST_SMS_SENDER)
    logger.info("Celery test SMS sent to {}", phone)

    return {"status": "sent", "phone": phone}
