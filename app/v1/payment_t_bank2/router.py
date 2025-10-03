import hashlib
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

# --- Конфиг ---
# T_BANK_API_URL = "https://rest-api-test.tinkoff.ru/v2"
T_BANK_API_URL = "https://securepay.tinkoff.ru/v2"
T_BANK_TERMINAL_KEY = "1752237644677DEMO"
T_BANK_PASSWORD = "bniUwpLIsj1^VkGC"

v1_t_bank_router_2 = APIRouter()


# --- Схемы ---
class CreatePaymentRequest(BaseModel):
    order_id: str
    amount: int  # в копейках
    description: str
    method: Optional[str] = "card"  # card | sbp


class TBankWebhook(BaseModel):
    TerminalKey: str
    OrderId: str
    Success: bool
    Status: str
    PaymentId: str
    ErrorCode: str
    Amount: int
    Token: str


# --- Клиент банка ---
class TBankClient:
    def __init__(self, terminal_key: str, password: str, base_url: str = T_BANK_API_URL):
        self.terminal_key = terminal_key
        self.password = password
        self.base_url = base_url

    def _generate_token(self, payload: dict) -> str:
        """Собираем токен: сортировка + sha256"""
        payload_with_password = {**payload, "Password": self.password}
        sorted_items = sorted(payload_with_password.items())
        values_str = "".join(str(v) for _, v in sorted_items if v is not None)
        return hashlib.sha256(values_str.encode("utf-8")).hexdigest()

    async def _send_request(self, endpoint: str, payload: dict) -> dict:
        payload["TerminalKey"] = self.terminal_key
        payload["Token"] = self._generate_token(payload)

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/{endpoint}", json=payload, headers=headers)

        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"T-Bank API error {resp.status_code}")

        data = resp.json()
        if not data.get("Success", False):
            raise HTTPException(status_code=400, detail=data)
        return data

    async def init_payment(self, order_id: str, amount: int, description: str, method: str = "card") -> dict:
        """Создание платежа"""
        payload = {
            "OrderId": order_id,
            "Amount": amount,
            "Description": description,
            "NotificationURL": "https://yourdomain.com/payments/webhook",
        }

        if method == "sbp":
            return await self._send_request("AddAccountQr", payload)
        else:
            return await self._send_request("Init", payload)

    async def charge_payment(self, payment_id: str, rebill_id: str) -> dict:
        """Автосписание по сохранённой карте"""
        payload = {
            "PaymentId": payment_id,
            "RebillId": rebill_id,
        }
        return await self._send_request("Charge", payload)


# --- Роуты ---
@v1_t_bank_router_2.post("/create")
async def create_payment(data: CreatePaymentRequest):
    client = TBankClient(T_BANK_TERMINAL_KEY, T_BANK_PASSWORD)
    result = await client.init_payment(
        order_id=data.order_id,
        amount=data.amount,
        description=data.description,
        method=data.method,
    )

    # SBP → отдадим QR
    if data.method == "sbp":
        return {
            "qrUrl": result.get("Data", {}).get("Payload"),
            "paymentId": result.get("PaymentId"),
        }

    return {"paymentUrl": result["PaymentURL"], "paymentId": result["PaymentId"]}


@v1_t_bank_router_2.post("/webhook")
async def payment_webhook(request: Request):
    body = await request.json()
    webhook = TBankWebhook(**body)

    # проверяем подпись
    client = TBankClient(T_BANK_TERMINAL_KEY, T_BANK_PASSWORD)
    expected_token = client._generate_token({k: v for k, v in body.items() if k != "Token"})

    if webhook.Token != expected_token:
        raise HTTPException(status_code=400, detail="Invalid token in webhook")

    if webhook.Success and webhook.Status == "CONFIRMED":
        print(f"✅ Заказ {webhook.OrderId} успешно оплачен {webhook.Amount}")
        # тут можно обновить заказ в БД
    else:
        print(f"⚠ Оплата заказа {webhook.OrderId} не удалась: {webhook.Status}")

    return {"status": "ok"}
