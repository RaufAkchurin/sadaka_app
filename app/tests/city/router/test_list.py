class TestCityList:
    async def test_400_authorization(self, ac) -> None:
        response = await ac.get("/app/v1/cities/all")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    async def test_list(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.get("/app/v1/cities/all", cookies=auth_ac_super.cookies.dict())
        assert response.status_code == 200

        assert response.json() == {
            "items": [{"id": 1, "name": "Kazan"}, {"id": 2, "name": "Ufa"}, {"id": 3, "name": "Ishim"}],
            "state": {"page": 1, "size": 5, "total_items": 3, "total_pages": 1},
        }
