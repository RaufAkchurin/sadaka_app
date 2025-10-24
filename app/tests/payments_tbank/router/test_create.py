from app.v1.payment_tinkoff.schemas import TBankPaymentMethodEnum


class TestTBANKPaymentCreate:
    project_id = 1
    amount = 10_00  # копейки

    async def test_400_without_token(self, ac) -> None:
        response = await ac.post(
            "/app/v1/payments/tbank/create",
            json={
                "amount": self.amount,
                "method": "card",
                "project_id": self.project_id,
            },
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    async def test_project_id_validate(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.post(
            "/app/v1/payments/tbank/create",
            cookies=auth_ac_super.cookies.dict(),
            json={"amount": self.amount, "method": "card", "project_id": 9999},
        )
        assert response.status_code == 422
        assert response.json()["detail"] == "Нет сущности с данным project_id."

    async def test_create_card(self, auth_ac_super, mocker) -> None:
        init_result = {"PaymentURL": "https://pay.tbank.ru/abc", "PaymentId": "pid-1"}
        mocker.patch("app.v1.payment_tinkoff.router.TBankClient.init_payment", return_value=init_result)

        response = await auth_ac_super.client.post(
            "/app/v1/payments/tbank/create",
            cookies=auth_ac_super.cookies.dict(),
            json={"amount": self.amount, "method": "card", "project_id": self.project_id},
        )

        assert response.status_code == 200
        assert response.json() == {"paymentUrl": "https://pay.tbank.ru/abc", "paymentId": "pid-1"}

    async def test_create_sbp(self, auth_ac_super, mocker) -> None:
        init_result = {"PaymentId": "pid-2", "QrPayload": "tbank-qr://payload"}
        mocker.patch("app.v1.payment_tinkoff.router.TBankClient.init_payment", return_value=init_result)

        response = await auth_ac_super.client.post(
            "/app/v1/payments/tbank/create",
            cookies=auth_ac_super.cookies.dict(),
            json={"amount": self.amount, "method": "sbp", "project_id": self.project_id},
        )

        assert response.status_code == 200
        assert response.json() == {"qrUrl": "tbank-qr://payload", "paymentId": "pid-2"}

    async def test_create_recurring_card(self, auth_ac_super, mocker) -> None:
        init_result = {"PaymentURL": "https://pay.tbank.ru/rec", "PaymentId": "pid-rec"}
        init_mock = mocker.patch("app.v1.payment_tinkoff.router.TBankClient.init_payment", return_value=init_result)

        response = await auth_ac_super.client.post(
            "/app/v1/payments/tbank/create_recurring",
            cookies=auth_ac_super.cookies.dict(),
            json={"amount": self.amount, "project_id": self.project_id},
        )

        assert response.status_code == 200
        assert response.json() == {"paymentUrl": "https://pay.tbank.ru/rec", "paymentId": "pid-rec"}
        init_mock.assert_awaited_once()
        called_kwargs = init_mock.await_args.kwargs
        assert called_kwargs["recurring"] is True
        assert called_kwargs["method"] == TBankPaymentMethodEnum.CARD

    async def test_create_recurring_rejects_non_card_method(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.post(
            "/app/v1/payments/tbank/create_recurring",
            cookies=auth_ac_super.cookies.dict(),
            json={"amount": self.amount, "project_id": self.project_id, "method": "sbp"},
        )

        assert response.status_code == 422
        detail = response.json().get("detail", [])
        assert detail
        assert detail[0]["loc"][-1] == "method"
