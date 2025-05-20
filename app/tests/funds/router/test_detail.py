class TestFundDetail:
    async def test_400_authorization(self, ac) -> None:
        response = await ac.get("/app/v1/funds/detail/1")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    async def test_id_validate(self, auth_ac) -> None:
        response = await auth_ac.client.get("/app/v1/funds/detail/hob", cookies=auth_ac.cookies.dict())
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "input": "hob",
                    "loc": ["path", "fund_id"],
                    "msg": "Input should be a valid integer, unable to parse string as an integer",
                    "type": "int_parsing",
                }
            ]
        }

    async def test_id_not_exist(self, auth_ac) -> None:
        response = await auth_ac.client.get("/app/v1/funds/detail/99", cookies=auth_ac.cookies.dict())
        assert response.status_code == 404

    async def test_detail(self, auth_ac) -> None:
        response = await auth_ac.client.get("/app/v1/funds/detail/1", cookies=auth_ac.cookies.dict())
        assert response.status_code == 200

        assert response.json() == {
            "address": "address1",
            "description": "desc1",
            "documents": [
                {
                    "id": 17,
                    "mime": "JPEG",
                    "name": "Документ 1 для Фонда 1",
                    "size": 123,
                    "type": "PICTURE",
                    "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/%D1%82%D0%B5%D1%81%D1%82%D0%BE%D0%B2%D1%8B%D0%B5%20%D0%BA%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D0%B8%2F%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-04-28%20%D0%B2%2014.38.56.png",  # noqa E501
                },
                {
                    "id": 18,
                    "mime": "JPEG",
                    "name": "Документ 2 для Фонда 1",
                    "size": 123,
                    "type": "PICTURE",
                    "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/%D1%82%D0%B5%D1%81%D1%82%D0%BE%D0%B2%D1%8B%D0%B5%20%D0%BA%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D0%B8%2F%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-04-28%20%D0%B2%2014.38.56.png",  # noqa E501
                },
            ],
            "hot_line": "+79176542281",
            "id": 1,
            "name": "fund1",
            "projects": [
                {
                    "active_stage_number": 2,
                    "collected_percentage": 20,
                    "fund": {"id": 1, "name": "fund1", "picture_url": None},
                    "goal": 10000,
                    "id": 1,
                    "name": "project1",
                    "pictures_list": [],
                    "status": "finished",
                    "total_collected": 2000,
                    "unique_sponsors": 1,
                },
                {
                    "active_stage_number": None,
                    "collected_percentage": 0,
                    "fund": {"id": 1, "name": "fund1", "picture_url": None},
                    "goal": 40000,
                    "id": 4,
                    "name": "project4",
                    "pictures_list": [],
                    "status": "active",
                    "total_collected": 0,
                    "unique_sponsors": 0,
                },
            ],
            "projects_count": 2,
            "region_name": "Tatarstan",
            "total_collected": 2000,
        }
