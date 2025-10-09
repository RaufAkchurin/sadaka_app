import asyncio
import time
from io import StringIO
from unittest.mock import patch

import pytest
from loguru import logger
from starlette.datastructures import Address

from app.models.payment import Payment
from app.tests.fixtures.dao import DaoSchemas

# TODO Тесты на другие типы коллбэков


class TestTbankPaymentCallback:
    callback_mock_success = {
        "Amount": 1000,
        "CardId": 610280382,
        "Data": {
            "Device": "Desktop",
            "DeviceBrowser": "Safari",
            "DeviceIframe": "false",
            "DeviceOs": "Mac OS",
            "DeviceWebView": "false",
            "REDIRECT": "false",
            "SEND_EMAIL": "N",
            "SaveCard": "false",
            "Source": "cards",
            "VeAuthRc": "00",
            "accept": "application/json",
            "connection_type": "PF",
            "connection_type_pf": "true",
            "isMIDSyncEnabled": "true",
            "order_id_unique_processed": "ignored",
            "payAction": "3DS",
            "paymentUrl": "https://pay.tbank.ru/EdLymlTe",
            "project_id": "1",
            "user_id": "1",
        },
        "ErrorCode": "0",
        "ExpDate": "1230",
        "OrderId": "63",
        "Pan": "430000******0777",
        "PaymentId": 7160853973,
        "Status": "CONFIRMED",
        "Success": True,
        "TerminalKey": "1752237644677DEMO",
        "Token": "2794408b52ecc7d5b241935353269db2f511cc146418e9d3a63cf450f19e7235",
    }
    valid_ip = "91.194.226.181"
    invalid_ip = "91.194.225.181"

    @patch("fastapi.Request.client", Address(valid_ip, 1234))  # For ip_security checker
    async def test_callback_success(self, auth_ac_super, session, dao: DaoSchemas) -> None:
        payment_dao = dao.payment
        payments: list[Payment] = await payment_dao.find_all()
        assert len(payments) == 6

        response = await auth_ac_super.client.post(
            "/app/v1/payments/tbank/callback",
            cookies=auth_ac_super.cookies.dict(),
            json=self.callback_mock_success,
        )
        assert response.status_code == 200

        payments: list[Payment] = await payment_dao.find_all()
        assert len(payments) == 7

        current_payment = payments[-1]
        assert current_payment.provider_payment_id == "7160853973"

        assert current_payment.project_id == 1
        assert current_payment.user_id == 1
        assert current_payment.stage_id == 2
        assert current_payment.amount == 1000.0

    @patch("fastapi.Request.client", Address(valid_ip, 1234))  # For ip_security checker
    async def test_callback_success_doubled_same_request(self, auth_ac_super, session, dao: DaoSchemas) -> None:
        payment_dao = dao.payment
        payments: list[Payment] = await payment_dao.find_all()
        assert len(payments) == 7

        # COLLECT ALL LOGS
        sink = StringIO()
        logger.add(sink, level="SUCCESS")

        response = await auth_ac_super.client.post(
            "/app/v1/payments/tbank/callback",
            cookies=auth_ac_super.cookies.dict(),
            json=self.callback_mock_success,
        )
        assert response.status_code == 200

        payments: list[Payment] = await payment_dao.find_all()
        assert len(payments) == 7

        current_payment = payments[-1]
        assert current_payment.provider_payment_id == "7160853973"

        # CHECK LOGS
        logs = sink.getvalue().lower()
        assert "запись уже имеется" in logs or "callback пропущен" in logs, logs

        logger.remove()  # обязательно очистить sink

    @patch("fastapi.Request.client", Address(invalid_ip, 1234))  # Not valid IP
    async def test_callback_ip_checker_403(self, ac) -> None:
        response = await ac.post(
            "/app/v1/payments/tbank/callback",
            json=self.callback_mock_success,
        )
        assert response.status_code == 403

    @patch("fastapi.Request.client", Address(valid_ip, 1234))
    async def test_callback_ip_checker_200(self, ac) -> None:
        response = await ac.post(
            "/app/v1/payments/tbank/callback",
            json=self.callback_mock_success,
        )
        assert response.status_code == 200

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(100, 40, 70)])
    async def test_rps(self, ac, num_requests, expected_rps, max_rps, dao: DaoSchemas) -> None:
        async def make_request():
            # make all the payment_id is unique

            payment_id = int(self.callback_mock_success["PaymentId"])
            self.callback_mock_success["PaymentId"] = str(payment_id + 1)

            response = await ac.post("/app/v1/payments/tbank/callback", json=self.callback_mock_success)

            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        payments_count = await dao.payment.count()
        assert payments_count == num_requests + 7

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        # необязательная проверка минимального порога
        assert rps > expected_rps

        # необязательная проверка максимального порога
        assert rps < max_rps
