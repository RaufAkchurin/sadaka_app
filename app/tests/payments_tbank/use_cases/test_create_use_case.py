import asyncio

import pytest
from fastapi import HTTPException

from app.v1.payment_tinkoff.schemas import TBankPaymentMethodEnum
from app.v1.payment_tinkoff.use_cases.create import TBankClient


class TestTBankClientInit:
    def test_init_payment_card_uses_init_only(self, mocker):
        client = TBankClient(terminal_key="test", password="secret", base_url="https://example.tbank.ru")
        init_response = {"Success": True, "PaymentURL": "https://pay.tbank.ru/example", "PaymentId": 100500}

        send_mock = mocker.patch.object(client, "_send_request", return_value=init_response)

        result = asyncio.run(
            client.init_payment(
                project_id=1,
                user_id=2,
                order_id="ord-1",
                amount=10_00,
                description="test",
                method=TBankPaymentMethodEnum.CARD,
                customer_email="user@example.com",
            )
        )

        # возвращаем то, что отдал API
        assert result is init_response

        send_mock.assert_called_once()
        endpoint, payload = send_mock.call_args.args
        assert endpoint == "Init"
        assert payload["Amount"] == 10_00
        assert payload["DATA"] == {"project_id": 1, "user_id": 2, "is_recurring": False}
        assert payload["Receipt"]["Items"][0]["Amount"] == 10_00
        assert payload["Receipt"]["Items"][0]["Quantity"] == 1
        assert payload["Receipt"]["Taxation"] == "usn_income"
        assert payload["Receipt"]["Email"] == "user@example.com"

    def test_init_payment_sbp_requests_qr_payload(self, mocker):
        client = TBankClient(terminal_key="test", password="secret", base_url="https://example.tbank.ru")
        init_response = {"Success": True, "PaymentURL": "https://pay", "PaymentId": 12345}
        qr_response = {"Success": True, "Data": {"Payload": "some-qr"}}

        send_mock = mocker.patch.object(client, "_send_request", side_effect=[init_response, qr_response])

        result = asyncio.run(
            client.init_payment(
                project_id=3,
                user_id=4,
                order_id="ord-2",
                amount=500_00,
                description="sbp test",
                method=TBankPaymentMethodEnum.SBP,
                customer_phone="+79001234567",
            )
        )

        assert result["QrPayload"] == "some-qr"
        assert result["PaymentId"] == init_response["PaymentId"]
        assert result["QrData"] == qr_response["Data"]

        assert send_mock.call_count == 2
        init_call_endpoint, init_payload = send_mock.call_args_list[0].args
        assert init_call_endpoint == "Init"
        assert init_payload["PayType"] == "SBP"
        assert init_payload["DATA"] == {"project_id": 3, "user_id": 4, "is_recurring": False}
        assert init_payload["Receipt"]["Items"][0]["Name"] == "sbp test"
        assert init_payload["Receipt"]["Phone"] == "+79001234567"
        assert "Email" not in init_payload["Receipt"]

        qr_call_endpoint, qr_payload = send_mock.call_args_list[1].args
        assert qr_call_endpoint == "GetQr"
        assert qr_payload == {"PaymentId": init_response["PaymentId"], "DataType": "PAYLOAD"}

    def test_init_payment_sbp_without_payload_raises(self, mocker):
        client = TBankClient(terminal_key="test", password="secret", base_url="https://example.tbank.ru")
        init_response = {"Success": True, "PaymentId": 1}
        qr_response = {"Success": True, "Data": {}}

        mocker.patch.object(client, "_send_request", side_effect=[init_response, qr_response])

        with pytest.raises(HTTPException) as excinfo:
            asyncio.run(
                client.init_payment(
                    project_id=1,
                    user_id=1,
                    order_id="ord-3",
                    amount=100,
                    description="sbp fail",
                    method=TBankPaymentMethodEnum.SBP,
                    customer_email="fail@example.com",
                )
            )

        assert excinfo.value.status_code == 500
        assert "did not return SBP QR payload" in str(excinfo.value.detail)

    def test_init_payment_without_contact_uses_default_email(self, mocker):
        client = TBankClient(terminal_key="test", password="secret", base_url="https://example.tbank.ru")
        init_response = {"Success": True, "PaymentURL": "https://pay.tbank.ru/example", "PaymentId": 42}

        send_mock = mocker.patch.object(client, "_send_request", return_value=init_response)

        result = asyncio.run(
            client.init_payment(
                project_id=7,
                user_id=8,
                order_id="ord-5",
                amount=20_00,
                description="support",
            )
        )

        assert result is init_response
        send_mock.assert_called_once()
        _, payload = send_mock.call_args.args
        assert payload["Receipt"]["Email"] == "support@sdkapp.ru"
        assert "Phone" not in payload["Receipt"]
