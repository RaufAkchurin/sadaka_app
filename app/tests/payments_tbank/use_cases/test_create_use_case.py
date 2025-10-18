import asyncio
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.v1.payment_tinkoff.schemas import TBankPaymentMethodEnum
from app.v1.payment_tinkoff.use_cases.create import TBankClient


class TestTBankClientInit:
    def test_init_payment_card_uses_init_only(self):
        client = TBankClient(terminal_key="test", password="secret", base_url="https://example.tbank.ru")
        init_response = {"Success": True, "PaymentURL": "https://pay.tbank.ru/example", "PaymentId": 100500}

        with patch.object(client, "_send_request", return_value=init_response) as send_mock:
            result = asyncio.run(
                client.init_payment(
                    project_id=1,
                    user_id=2,
                    order_id="ord-1",
                    amount_rub=10,
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

    def test_init_payment_sbp_requests_qr_payload(self):
        client = TBankClient(terminal_key="test", password="secret", base_url="https://example.tbank.ru")
        init_response = {"Success": True, "PaymentURL": "https://pay", "PaymentId": 12345}
        qr_response = {"Success": True, "Data": {"Payload": "some-qr"}}

        with patch.object(client, "_send_request", side_effect=[init_response, qr_response]) as send_mock:
            result = asyncio.run(
                client.init_payment(
                    project_id=3,
                    user_id=4,
                    order_id="ord-2",
                    amount_rub=500,
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

    def test_init_payment_sbp_without_payload_raises(self):
        client = TBankClient(terminal_key="test", password="secret", base_url="https://example.tbank.ru")
        init_response = {"Success": True, "PaymentId": 1}
        qr_response = {"Success": True, "Data": {}}

        with patch.object(client, "_send_request", side_effect=[init_response, qr_response]):
            with pytest.raises(HTTPException) as excinfo:
                asyncio.run(
                    client.init_payment(
                        project_id=1,
                        user_id=1,
                        order_id="ord-3",
                        amount_rub=1,
                        description="sbp fail",
                        method=TBankPaymentMethodEnum.SBP,
                        customer_email="fail@example.com",
                    )
                )

        assert excinfo.value.status_code == 500
        assert "did not return SBP QR payload" in str(excinfo.value.detail)

    def test_init_payment_without_contact_uses_default_email(self):
        client = TBankClient(terminal_key="test", password="secret", base_url="https://example.tbank.ru")
        init_response = {"Success": True, "PaymentURL": "https://pay.tbank.ru/example", "PaymentId": 42}

        with patch.object(client, "_send_request", return_value=init_response) as send_mock:
            result = asyncio.run(
                client.init_payment(
                    project_id=7,
                    user_id=8,
                    order_id="ord-5",
                    amount_rub=20,
                    description="support",
                )
            )

        assert result is init_response
        send_mock.assert_called_once()
        _, payload = send_mock.call_args.args
        assert payload["Receipt"]["Email"] == "support@sdkapp.ru"
        assert "Phone" not in payload["Receipt"]

    def test_init_payment_recurring_adds_flags(self):
        client = TBankClient(terminal_key="test", password="secret", base_url="https://example.tbank.ru")
        init_response = {"Success": True, "PaymentURL": "https://pay.tbank.ru/example", "PaymentId": 24}

        with patch.object(client, "_send_request", return_value=init_response) as send_mock:
            result = asyncio.run(
                client.init_payment(
                    project_id=9,
                    user_id=10,
                    order_id="ord-rec",
                    amount_rub=30,
                    description="recurring",
                    recurring=True,
                )
            )

        assert result is init_response
        send_mock.assert_called_once()
        _, payload = send_mock.call_args.args
        assert payload["Recurrent"] == "Y"
        assert payload["OperationInitiatorType"] == "1"
        assert payload["DATA"] == {"project_id": 9, "user_id": 10, "is_recurring": True}

    def test_init_payment_for_rebilling_disables_recurring(self):
        client = TBankClient(terminal_key="test", password="secret", base_url="https://example.tbank.ru")
        init_response = {"Success": True, "PaymentURL": "https://pay.tbank.ru/example", "PaymentId": 55}

        with patch.object(client, "_send_request", return_value=init_response) as send_mock:
            result = asyncio.run(
                client.init_payment(
                    project_id=11,
                    user_id=12,
                    order_id="ord-no-rec",
                    amount_rub=40,
                    description="for rebilling",
                    recurring=True,
                    for_rebilling=True,
                )
            )

        assert result is init_response
        send_mock.assert_called_once()
        _, payload = send_mock.call_args.args
        assert "Recurrent" not in payload
        assert "OperationInitiatorType" not in payload
        assert payload["DATA"] == {"project_id": 11, "user_id": 12, "is_recurring": False}


class TestTBankClientInternals:
    def test_generate_token_skips_receipt_and_data(self):
        client = TBankClient(terminal_key="test", password="secret", base_url="https://example.tbank.ru")

        fake_hasher = MagicMock()
        fake_hasher.hexdigest.return_value = "digest"
        with patch("app.v1.payment_tinkoff.use_cases.create.hashlib.sha256", return_value=fake_hasher) as sha_mock:
            payload = {
                "Amount": 500,
                "CustomerKey": "user-1",
                "DATA": {"ignored": "data"},
                "Receipt": {"ignored": "receipt"},
                "Nested": {"foo": "bar"},
                "Optional": None,
            }

            token = client._generate_token(payload)

        assert token == "digest"
        sha_mock.assert_called_once()
        values_bytes = sha_mock.call_args.args[0]
        values_str = values_bytes.decode("utf-8")

        assert "ignored" not in values_str  # DATA/Receipt не участвуют в подписи
        assert '{"foo":"bar"}' in values_str  # словарь сериализуется
        assert "user-1" in values_str

    def test_send_request_raises_on_http_error(self):
        client = TBankClient(terminal_key="test", password="secret", base_url="https://example.tbank.ru")

        class DummyResponse:
            def __init__(self, status_code, payload):
                self.status_code = status_code
                self._payload = payload

            def json(self):
                return self._payload

        response = DummyResponse(status_code=502, payload={"Success": False})

        class DummyAsyncClient:
            def __init__(self, resp):
                self.response = resp
                self.calls = []

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

            async def post(self, *args, **kwargs):
                self.calls.append((args, kwargs))
                return self.response

        dummy_client = DummyAsyncClient(response)
        with patch("app.v1.payment_tinkoff.use_cases.create.httpx.AsyncClient", return_value=dummy_client):
            with pytest.raises(HTTPException) as excinfo:
                asyncio.run(client._send_request("Init", {"Amount": 100}))

        assert excinfo.value.status_code == 500
        assert excinfo.value.detail == "T-Bank API error 502"
        assert dummy_client.calls, "httpx.AsyncClient.post не вызывался"

    def test_send_request_raises_on_failed_success_flag(self):
        client = TBankClient(terminal_key="test", password="secret", base_url="https://example.tbank.ru")

        class DummyResponse:
            def __init__(self, status_code, payload):
                self.status_code = status_code
                self._payload = payload

            def json(self):
                return self._payload

        response = DummyResponse(status_code=200, payload={"Success": False, "ErrorCode": "123"})

        class DummyAsyncClient:
            def __init__(self, resp):
                self.response = resp
                self.calls = []

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

            async def post(self, *args, **kwargs):
                self.calls.append((args, kwargs))
                return self.response

        dummy_client = DummyAsyncClient(response)
        with patch("app.v1.payment_tinkoff.use_cases.create.httpx.AsyncClient", return_value=dummy_client):
            with pytest.raises(HTTPException) as excinfo:
                asyncio.run(client._send_request("Init", {"Amount": 200}))

        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == {"Success": False, "ErrorCode": "123"}
        assert dummy_client.calls, "httpx.AsyncClient.post не вызывался"
