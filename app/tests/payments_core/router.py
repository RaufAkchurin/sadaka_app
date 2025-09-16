class TestMyDonations:
    async def test_my_donations(self, ac, auth_ac_super, query_counter) -> None:
        response = await auth_ac_super.client.get("/app/v1/payments/my_donations", cookies=auth_ac_super.cookies.dict())
        assert response.status_code == 200

        assert len(query_counter) <= 11, f"Слишком много SQL-запросов: {len(query_counter)}"

        data = response.json()

        assert data is not None

        assert data["items"][0] is not None
        assert data["items"][0].get("amount") == 1100.0
        assert data["items"][0].get("project_name") == "project1"
        assert data["items"][0].get("created_at") is not None

        assert data["items"][1] is not None
        assert data["items"][1].get("amount") == 1200.0
        assert data["items"][1].get("project_name") == "project1"
        assert data["items"][1].get("created_at") is not None
