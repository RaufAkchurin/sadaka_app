class TestTBANKPaymentCreate:
    project_id = 1
    amount = 1000

    async def test_400_authorization(self, ac) -> None:
        response = await ac.post(
            "/app/v1/payments/tbank/create",
            json={
                "order_id": "string",
                "amount": self.amount * 100,
                "description": "string",
                "method": "card",
                "project_id": self.project_id,
                "user_id": 1,
            },
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    async def test_project_id_validate(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.post(
            f"/app/v1/payments/yookassa/{99}/{self.amount}", cookies=auth_ac_super.cookies.dict()
        )
        assert response.status_code == 422

    async def test_create(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.post(
            f"/app/v1/payments/yookassa/{1}/{self.amount}", cookies=auth_ac_super.cookies.dict()
        )
        assert response.status_code == 200
        assert "https://yoomoney.ru/checkout/payments/v2/contract?orderId=" in response.json().get("redirect_url", None)
