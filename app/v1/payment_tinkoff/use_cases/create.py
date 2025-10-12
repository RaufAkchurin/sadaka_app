import hashlib

import httpx
from fastapi import HTTPException

from app.settings import settings


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

        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/{endpoint}", json=payload, headers=headers)

        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"T-Bank API error {resp.status_code}")

        data = resp.json()
        if not data.get("Success", False):
            raise HTTPException(status_code=400, detail=data)
        return data

    async def init_payment(
        self,
        project_id: int,
        user_id: int,
        order_id: str,
        amount: int,
        description: str,
        method: str = "card",
    ) -> dict:
        if method == "sbp":
            payload = {
                "OrderId": order_id,
                "Description": description,
                "NotificationURL": settings.T_BANK_WEBHOOK_URL,
            }
            return await self._send_request("AddAccountQr", payload)
        else:
            payload = {
                "OrderId": order_id,
                "Amount": amount,
                "Description": description,
                "NotificationURL": settings.T_BANK_WEBHOOK_URL,
                "DATA": {
                    "project_id": project_id,
                    "user_id": user_id,
                },
            }

            return await self._send_request("Init", payload)

    async def charge_payment(self, payment_id: str, rebill_id: str) -> dict:
        """Автосписание по сохранённой карте"""
        payload = {
            "PaymentId": payment_id,
            "RebillId": rebill_id,
        }
        return await self._send_request("Charge", payload)
