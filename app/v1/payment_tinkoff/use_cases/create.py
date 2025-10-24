import hashlib
import json
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

    # def _build_receipt(
    #     self,
    #     description: str,
    #     amount: int,
    #     customer_email: str | None,
    #     customer_phone: str | None,
    # ) -> dict[str, Any]:
    #     """Минимально допустимый чек для Init: одна позиция на всю сумму + контакт."""
    #     sanitized_name = (description or "Платеж").strip() or "Платеж"
    #     receipt: dict[str, Any] = {
    #         "Items": [
    #             {
    #                 "Name": sanitized_name[:128],
    #                 "Price": amount,
    #                 "Quantity": 1,
    #                 "Amount": amount,
    #                 "PaymentMethod": "full_payment",
    #                 "PaymentObject": "service",
    #                 "Tax": "none",
    #             }
    #         ],
    #         "Taxation": "usn_income",
    #     }
    #     if customer_email:
    #         receipt["Email"] = customer_email
    #     elif not customer_phone:
    #         receipt["Email"] = "support@sdkapp.ru"
    #
    #     if customer_phone:
    #         receipt["Phone"] = customer_phone
    #     return receipt

    def _generate_token(self, payload: dict) -> str:
        """Собираем токен: сортировка + sha256"""
        payload_with_password = {**payload, "Password": self.password}
        sorted_items = sorted(payload_with_password.items())
        values = []
        for key, value in sorted_items:
            if value is None or key in ["DATA", "Receipt"]:
                continue
            if isinstance(value, dict):
                values.append(json.dumps(value, ensure_ascii=False, separators=(",", ":")))
            else:
                values.append(str(value))
        values_str = "".join(values)
        logger.info(f"T-Bank token payload: {values_str}")
        return hashlib.sha256(values_str.encode("utf-8")).hexdigest()

    async def _send_request(self, endpoint: str, payload: dict) -> dict:
        payload["TerminalKey"] = self.terminal_key
        payload["Token"] = self._generate_token(payload)

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        logger.info(f"request_url: {self.base_url}/{endpoint}")
        logger.info(f"request_data: {payload}")
        logger.info(f"request_headers: {headers}")

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
        method: TBankPaymentMethodEnum | Literal["card", "sbp"] = TBankPaymentMethodEnum.CARD,# CARD get all methods
        recurring: bool = False,
        for_rebilling: bool = False,
        customer_email: str | None = None, # for receipt
        customer_phone: str | None = None, # for receipt
    ) -> dict[str, Any]:
        method_value = method.value if isinstance(method, TBankPaymentMethodEnum) else method

        effective_recurring = False if for_rebilling else recurring

        # receipt = self._build_receipt(
        #     description=description,
        #     amount=amount,
        #     customer_email=customer_email,
        #     customer_phone=customer_phone,
        # )

        base_payload: dict[str, Any] = {
            "OrderId": order_id,
            "Amount": amount,
            "Description": description,
            "NotificationURL": settings.T_BANK_WEBHOOK_URL,
            "CustomerKey": str(user_id),
            "DATA": {
                "project_id": project_id,
                "user_id": user_id,
                "is_recurring": effective_recurring,
            },
            # "Receipt": receipt,
        }

        if effective_recurring:
            base_payload["Recurrent"] = "Y"
            base_payload["OperationInitiatorType"] = "1"

        if method_value == TBankPaymentMethodEnum.SBP.value:
            init_response = await self._send_request("Init", base_payload)
            qr_response = await self._send_request(
                "GetQr",
                {
                    "PaymentId": init_response["PaymentId"],
                    "DataType": "PAYLOAD",
                },
            )

            logger.info(f"T-Bank qr_response: {qr_response}")
            qr_payload = qr_response.get("Data", {})


            init_response["QrPayload"] = qr_payload
            init_response["QrData"] = qr_response.get("Data")
            return init_response

        logger.info(f"T-Bank payload: {base_payload}")

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
