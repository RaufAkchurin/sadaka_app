import uuid

from models.payment import Payment
from v1.dependencies.dao_dep import get_session_with_commit
from v1.users.dao import PaymentDAO


class TestPaymentCallback:
    async def test_callback_complete(self, auth_ac) -> None:
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
            "captured_at": "2025-05-26T09:59:37.989Z",
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

        response = await auth_ac.client.post(
            "/app/v1/payments/yookassa_callback", json={"object": callback_mock_success}, cookies=auth_ac.cookies.dict()
        )
        assert response.status_code == 200

        session_gen = get_session_with_commit()
        session = await session_gen.__anext__()

        payment_dao = PaymentDAO(session=session)
        payments: list[Payment] = await payment_dao.find_all()
        assert len(payments) == 1

        current_payment = payments[-1]
        assert current_payment.id == uuid.UUID("2fc64f42-000f-5000-8000-14945ca734f5")

        assert current_payment.project_id == 1
        assert current_payment.stage_id == 2
        assert current_payment.amount == 32.0
