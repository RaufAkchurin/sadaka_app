import asyncio
import time
import uuid
from unittest.mock import patch

import pytest
from loguru import logger
from starlette.datastructures import Address

from app.models.payment import Payment
from app.tests.fixtures.dao import DaoSchemas
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.users.dao import PaymentDAO


class TestYOOKASSAPaymentCallback:
    callback_mock_success = {
        "amount": {"currency": "RUB", "value": "32.00"},
        "authorization_details": {
            "auth_code": "235381",
            "rrn": "703693542966385",
            "three_d_secure": {
                "applied": False,
                "challenge_completed": False,
                "method_completed": False,
            },
        },
        "created_at": "2025-05-26T09:59:30.251Z",
        "description": "Проект Строительство мечети, айди 22",
        "id": "2fc64f42-000f-5000-8000-14945ca734f5",
        "income_amount": {"currency": "RUB", "value": "30.88"},
        "metadata": {
            "payment_id": 1,
            "project_id": 1,
            "user_id": 1,
        },
        "paid": True,
        "payment_method": {
            "card": {
                "card_product": {"code": "E"},
                "card_type": "MasterCard",
                "expiry_month": "12",
                "expiry_year": "2027",
                "first6": "555555",
                "issuer_country": "US",
                "last4": "4444",
            },
            "id": "2fc64f42-000f-5000-8000-14945ca734f5",
            "saved": False,
            "status": "inactive",
            "title": "Bank card *4444",
            "type": "bank_card",
        },
        "recipient": {"account_id": "469140", "gateway_id": "2324047"},
        "refundable": True,
        "refunded_amount": {"currency": "RUB", "value": "0.00"},
        "status": "succeeded",
        "test": True,
    }

    # TEST IT WORK BUT NOT IN SCOPE AND RUN SINGULAR
    @patch("fastapi.Request.client", Address("185.71.76.1", 1234))  # For ip_security checker
    async def test_callback_cancelled(self, auth_ac_super) -> None:
        # TODO РПОБЛЕМА С ЗАПУСКОМ ДВУХ ТЕСТОВ ОДНОВРЕМЕННО - с сессией какая то фигня
        callback_mock_canceled = self.callback_mock_success
        callback_mock_canceled["status"] = "canceled"

        response = await auth_ac_super.client.post(
            "/app/v1/payments/yookassa/callback",
            cookies=auth_ac_super.cookies.dict(),
            json={"object": callback_mock_canceled},
        )
        assert response.status_code == 200

        session_gen = get_session_with_commit()
        session = await session_gen.__anext__()

        payment_dao = PaymentDAO(session=session)
        payments: list[Payment] = await payment_dao.find_all()
        assert len(payments) == 6  # sum of mocked data without new

    @patch("fastapi.Request.client", Address("185.71.76.1", 1234))  # For ip_security checker
    async def test_callback_success(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.post(
            "/app/v1/payments/yookassa/callback",
            cookies=auth_ac_super.cookies.dict(),
            json={"object": self.callback_mock_success},
        )
        assert response.status_code == 200

        session_gen = get_session_with_commit()
        session = await session_gen.__anext__()

        payment_dao = PaymentDAO(session=session)
        payments: list[Payment] = await payment_dao.find_all()
        assert len(payments) == 7

        current_payment = payments[-1]
        assert current_payment.provider_payment_id == str(uuid.UUID("2fc64f42-000f-5000-8000-14945ca734f5"))

        assert current_payment.project_id == 1
        assert current_payment.user_id == 1
        assert current_payment.stage_id == 2
        assert current_payment.amount == 32.0

    async def test_callback_ip_checker_403(self, ac) -> None:
        response = await ac.post("/app/v1/payments/yookassa/callback", json={"object": self.callback_mock_success})
        assert response.status_code == 403

    @patch("fastapi.Request.client", Address("185.71.76.1", 1234))
    async def test_callback_ip_checker_200(self, ac) -> None:
        response = await ac.post("/app/v1/payments/yookassa/callback", json={"object": self.callback_mock_success})
        assert response.status_code == 200

    @patch("fastapi.Request.client", Address("185.71.76.1", 1234))  # For ip_security checker
    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(100, 40, 70)])
    async def test_rps(self, ac, num_requests, expected_rps, max_rps, dao: DaoSchemas) -> None:
        async def make_request():
            self.callback_mock_success["id"] = str(uuid.uuid4())  # make all the payment_id is unique

            response = await ac.post("/app/v1/payments/yookassa/callback", json={"object": self.callback_mock_success})

            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        payments_count = await dao.payment.count()
        assert payments_count == 106

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        # необязательная проверка минимального порога
        assert rps > expected_rps

        # необязательная проверка максимального порога
        assert rps < max_rps
