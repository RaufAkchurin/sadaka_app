import json

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

v1_t_bank_router_2 = APIRouter()

# Конфиг (лучше хранить в env)
# T_BANK_API_URL = "https://securepay.tinkoff.ru/v2"  # у тебя будет актуальный url
T_BANK_API_URL = "https://rest-api-test.tinkoff.ru/v2"  # у тебя будет актуальный url
T_BANK_TERMINAL_KEY = "1752237644677DEMO"
T_BANK_PASSWORD = "bniUwpLIsj1^VkGC"

# --- Схемы ---


class CreatePaymentRequest(BaseModel):
    order_id: str
    amount: int  # в копейках/центах (например, 10000 = 100.00 руб)
    description: str


class TBankWebhook(BaseModel):
    TerminalKey: str
    OrderId: str
    Success: bool
    Status: str
    PaymentId: str
    ErrorCode: str
    Amount: int


# --- Эндпоинт для создания платежа ---
@v1_t_bank_router_2.post("/payments/create")
async def create_payment(data: CreatePaymentRequest):
    payload = {
        "TerminalKey": T_BANK_TERMINAL_KEY,
        "Password": T_BANK_PASSWORD,
        "OrderId": data.order_id,
        "Amount": data.amount,
        "Description": data.description,
        "NotificationURL": "https://yourdomain.com/payments/webhook"  # вебхук
        # "SuccessURL": "https://yourfrontend.com/payment/success",
        # "FailURL": "https://yourfrontend.com/payment/fail",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{T_BANK_API_URL}/Init", json=payload)

    if not resp.status_code != 200:
        raise HTTPException(status_code=400)

    # отдаём фронту ссылку для редиректа/открытия WebView
    result = json.loads(resp.text)
    return {"paymentUrl": result["PaymentURL"], "paymentId": result["PaymentId"]}


# --- Вебхук от Т-Банка ---
@v1_t_bank_router_2.post("/payments/webhook")
async def payment_webhook(request: Request):
    body = await request.json()
    webhook = TBankWebhook(**body)

    # тут можно проверить подпись (если банк требует)

    if webhook.Success and webhook.Status == "CONFIRMED":
        # обновляем заказ в БД как оплаченный
        print(f"✅ Заказ {webhook.OrderId} успешно оплачен {webhook.Amount}")
    else:
        print(f"⚠ Оплата заказа {webhook.OrderId} не удалась: {webhook.Status}")

    return {"status": "ok"}  # банк ждет 200 OK
