# main.py
import logging
from typing import Any, Dict

from fastapi import BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse
from storage import payment_storage

from app.main import app
from app.v1.payment_t_bank.schemas import CreatePaymentRequest, PaymentResponse, PaymentStatus
from app.v1.payment_t_bank.service import TBankService

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tbank_service = TBankService()


@app.post("/payments/create", response_model=PaymentResponse)
async def create_payment(payment_request: CreatePaymentRequest, background_tasks: BackgroundTasks):
    """Создание нового платежа"""

    # Создаем запись о платеже в нашем хранилище
    payment = payment_storage.create_payment(
        amount=payment_request.amount, order_id=payment_request.order_id, user_id=payment_request.user_id
    )

    # URL для редиректа после оплаты
    success_url = f"https://yourapp.com/payments/success?payment_id={payment.payment_id}"
    fail_url = f"https://yourapp.com/payments/fail?payment_id={payment.payment_id}"

    # Создаем платеж в TBank
    tbank_response = await tbank_service.create_payment(payment_request, success_url, fail_url)

    if not tbank_response.Success:
        logger.error(f"Failed to create payment in TBank: {tbank_response.ErrorMessage}")
        raise HTTPException(status_code=400, detail=f"Payment creation failed: {tbank_response.ErrorMessage}")

    # Обновляем платеж с URL для оплаты
    payment_storage.update_payment_status(payment.payment_id, PaymentStatus.PENDING, tbank_response.PaymentURL)

    logger.info(f"Payment created: {payment.payment_id}, Order: {payment_request.order_id}")

    return PaymentResponse(
        payment_id=payment.payment_id,
        status=payment.status,
        payment_url=tbank_response.PaymentURL,
        amount=payment.amount,
        order_id=payment.order_id,
        created_at=payment.created_at,
    )


@app.post("/webhook/tbank")
async def tbank_webhook(request: Request, background_tasks: BackgroundTasks):
    """Вебхук для получения уведомлений о статусе платежей от TBank"""

    try:
        webhook_data = await request.json()
        logger.info(f"Received webhook: {webhook_data}")

        # Проверяем подпись (если требуется TBank)
        signature = request.headers.get("X-Signature")
        if signature and not tbank_service.verify_webhook_signature(webhook_data, signature):
            logger.warning("Invalid webhook signature")
            return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid signature"})

        # Обрабатываем вебхук в фоновом режиме
        background_tasks.add_task(process_webhook, webhook_data)

        return {"status": "success", "message": "Webhook processed"}

    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return JSONResponse(status_code=400, content={"status": "error", "message": str(e)})


async def process_webhook(webhook_data: Dict[str, Any]):
    """Фоновая обработка вебхука"""
    try:
        payment_id = webhook_data.get("PaymentID")
        order_id = webhook_data.get("OrderID")
        status = webhook_data.get("Status")
        amount = webhook_data.get("Amount")

        if not payment_id or not order_id:
            logger.error("Missing required fields in webhook")
            return

        # Конвертируем статус TBank в наш внутренний статус
        internal_status = convert_tbank_status(status)

        # Обновляем статус платежа в нашем хранилище
        if payment_storage.update_payment_status(payment_id, internal_status):
            logger.info(f"Payment {payment_id} status updated to {internal_status}")

            # Здесь можно добавить дополнительную логику:
            # - Отправка уведомлений пользователю
            # - Обновление заказа в БД
            # - Начисление услуг и т.д.

            if internal_status == PaymentStatus.SUCCESS:
                await handle_successful_payment(payment_id, order_id, amount)
            elif internal_status == PaymentStatus.FAILED:
                await handle_failed_payment(payment_id, order_id)

        else:
            logger.warning(f"Payment {payment_id} not found in storage")

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")


def convert_tbank_status(tbank_status: str) -> PaymentStatus:
    """Конвертация статуса TBank во внутренний статус"""
    status_mapping = {
        "SUCCESS": PaymentStatus.SUCCESS,
        "FAILED": PaymentStatus.FAILED,
        "CANCELLED": PaymentStatus.CANCELLED,
        "PENDING": PaymentStatus.PENDING,
    }
    return status_mapping.get(tbank_status.upper(), PaymentStatus.PENDING)


async def handle_successful_payment(payment_id: str, order_id: str, amount: float):
    """Обработка успешного платежа"""
    logger.info(f"Payment {payment_id} for order {order_id} completed successfully")
    # TODO: Реализовать бизнес-логику для успешного платежа
    # - Активировать услуги
    # - Отправить уведомление
    # - Обновить статус заказа и т.д.


async def handle_failed_payment(payment_id: str, order_id: str):
    """Обработка неуспешного платежа"""
    logger.warning(f"Payment {payment_id} for order {order_id} failed")
    # TODO: Реализовать логику для неудачного платежа


@app.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment_status(payment_id: str):
    """Получение статуса платежа"""
    payment = payment_storage.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "healthy", "service": "TBank Integration"}
