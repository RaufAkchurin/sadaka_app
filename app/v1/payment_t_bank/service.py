# tbank_service.py
import hashlib
import hmac
from typing import Any, Dict

import httpx

from app.settings import settings
from app.v1.payment_t_bank.schemas import CreatePaymentRequest, TBankPaymentResponse


class TBankService:
    def __init__(self):
        self.base_url = settings.tbank_base_url
        self.merchant_id = settings.tbank_merchant_id
        self.terminal_id = settings.tbank_terminal_id
        self.secret_key = settings.tbank_secret_key

    def _generate_signature(self, data: Dict[str, Any]) -> str:
        """Генерация подписи для TBank API"""
        # Сортируем ключи в алфавитном порядке
        sorted_data = dict(sorted(data.items()))

        # Создаем строку для подписи
        sign_string = ""
        for key, value in sorted_data.items():
            if value is not None:
                sign_string += f"{key}={value}&"

        # Убираем последний &
        sign_string = sign_string[:-1]

        # Добавляем секретный ключ
        sign_string += self.secret_key

        # Создаем HMAC-SHA256 подпись
        signature = hmac.new(self.secret_key.encode("utf-8"), sign_string.encode("utf-8"), hashlib.sha256).hexdigest()

        return signature

    async def create_payment(
        self, payment_data: CreatePaymentRequest, success_url: str, fail_url: str
    ) -> TBankPaymentResponse:
        """Создание платежа в TBank"""

        # Подготавливаем данные для TBank
        tbank_request_data = {
            "MerchantID": self.merchant_id,
            "TerminalID": self.terminal_id,
            "Amount": str(int(payment_data.amount * 100)),  # Конвертируем в копейки
            "Currency": payment_data.currency,
            "OrderID": payment_data.order_id,
            "Description": payment_data.description,
            "SuccessURL": success_url,
            "FailURL": fail_url,
        }

        # Генерируем подпись
        signature = self._generate_signature(tbank_request_data)
        tbank_request_data["Signature"] = signature

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/payment/create",
                    json=tbank_request_data,
                    headers={"Content-Type": "application/json"},
                )

                response_data = response.json()

                return TBankPaymentResponse(
                    Success=response_data.get("Success", False),
                    PaymentID=response_data.get("PaymentID"),
                    PaymentURL=response_data.get("PaymentURL"),
                    ErrorCode=response_data.get("ErrorCode"),
                    ErrorMessage=response_data.get("ErrorMessage"),
                )

            except Exception as e:
                return TBankPaymentResponse(Success=False, ErrorMessage=f"Network error: {str(e)}")

    def verify_webhook_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """Проверка подписи вебхука от TBank"""
        calculated_signature = self._generate_signature(data)
        return hmac.compare_digest(calculated_signature, signature)
