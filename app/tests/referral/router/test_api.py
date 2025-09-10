class TestReferrals:
    async def test_validator(self, ac, auth_ac, query_counter) -> None:
        response = await auth_ac.client.get("/app/v1/payments/my_donations", cookies=auth_ac.cookies.dict())
        assert response.status_code == 200

        assert len(query_counter) <= 11, f"Слишком много SQL-запросов: {len(query_counter)}"

        data = response.json()

        assert data is not None
