import hashlib
from typing import Any, Literal

import httpx
from fastapi import HTTPException
from loguru import logger

from app.settings import settings
from app.v1.payment_tinkoff.schemas import TBankPaymentMethodEnum


class TBankClient:
    def __init__(self, terminal_key: str, password: str, base_url: str = settings.T_BANK_API_URL):
        self.terminal_key = terminal_key
        self.password = password
        self.base_url = base_url

    def _generate_token(self, payload: dict) -> str:
        """Собираем токен: сортировка + sha256"""
        payload_with_password = {**payload, "Password": self.password}
        sorted_items = sorted(payload_with_password.items())
        values_str = "".join(str(v) for _, v in sorted_items if v is not None and _ != "DATA")
        return hashlib.sha256(values_str.encode("utf-8")).hexdigest()

    async def _send_request(self, endpoint: str, payload: dict) -> dict:
        payload["TerminalKey"] = self.terminal_key
        payload["Token"] = self._generate_token(payload)

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        logger.success(f"request_url: {self.base_url}/{endpoint}")
        logger.success(f"request_data: {payload}")
        logger.success(f"request_headers: {headers}")

        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/{endpoint}", json=payload, headers=headers)

        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"T-Bank API error {resp.status_code}")

        data = resp.json()
        if not data.get("Success", False):
            raise HTTPException(status_code=400, detail=data)

        logger.success(f"T-Bank response: {data}")
        return data

    async def init_payment(
        self,
        project_id: int,
        user_id: int,
        order_id: str,
        amount: int,
        description: str,
        method: TBankPaymentMethodEnum | Literal["card", "sbp"] = TBankPaymentMethodEnum.CARD,
        recurring: bool = False,
    ) -> dict[str, Any]:
        method_value = method.value if isinstance(method, TBankPaymentMethodEnum) else method

        base_payload: dict[str, Any] = {
            "OrderId": order_id,
            "Amount": amount,
            "Description": description,
            "NotificationURL": settings.T_BANK_WEBHOOK_URL,
            "CustomerKey": str(user_id),
            "DATA": {
                "project_id": project_id,
                "user_id": user_id,
                "is_recurring": recurring,
            },
        }

        if recurring:
            base_payload["Recurrent"] = "Y"
            base_payload["OperationInitiatorType"] = "1"

        if method_value == TBankPaymentMethodEnum.SBP.value:
            base_payload["PayType"] = "SBP"
            init_response = await self._send_request("Init", base_payload)

            qr_response = await self._send_request(
                "GetQr",
                {
                    "PaymentId": init_response["PaymentId"],
                    "DataType": "PAYLOAD",
                },
            )

            qr_payload = qr_response.get("Data", {}).get("Payload")
            if not qr_payload:
                raise HTTPException(status_code=500, detail="T-Bank API did not return SBP QR payload")

            init_response["QrPayload"] = qr_payload
            init_response["QrData"] = qr_response.get("Data")
            return init_response

        logger.success(f"T-Bank payload: {base_payload}")

        return await self._send_request("Init", base_payload)

    async def charge_payment(
        self,
        payment_id: int | str,
        rebill_id: int | str,
    ) -> dict[str, Any]:
        """Автосписание по сохранённой карте"""
        payload: dict[str, Any] = {
            "PaymentId": payment_id,
            "RebillId": rebill_id,
        }
        return await self._send_request("Charge", payload)
