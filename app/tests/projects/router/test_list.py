class TestProjectList:
    async def test_400_authorization(self, ac) -> None:
        response = await ac.get("/app/v1/projects/all/active")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    async def test_list_active(self, auth_ac) -> None:
        response = await auth_ac.client.get("/app/v1/projects/all/active", cookies=auth_ac.cookies.dict())
        assert response.status_code == 200

        assert response.json() == {
            "items": [
                {
                    "active_stage_number": 2,
                    "collected_percentage": 10,
                    "fund": {"id": 2, "name": "fund2", "picture_url": None},
                    "goal": 20000,
                    "id": 2,
                    "name": "project2",
                    "pictures_list": [],
                    "status": "active",
                    "total_collected": 2000,
                    "unique_sponsors": 1,
                },
                {
                    "active_stage_number": None,
                    "collected_percentage": 6,
                    "fund": {"id": 3, "name": "fund3", "picture_url": None},
                    "goal": 30000,
                    "id": 3,
                    "name": "project3",
                    "pictures_list": [],
                    "status": "active",
                    "total_collected": 2000,
                    "unique_sponsors": 1,
                },
            ],
            "state": {"page": 1, "size": 2, "total_items": 2, "total_pages": 1},
        }

    async def test_list_finished(self, auth_ac) -> None:
        response = await auth_ac.client.get("/app/v1/projects/all/finished", cookies=auth_ac.cookies.dict())

        assert response.status_code == 200
        assert response.json() == {
            "items": [
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
                    "status": "finished",
                    "total_collected": 0,
                    "unique_sponsors": 0,
                },
            ],
            "state": {"page": 1, "size": 2, "total_items": 2, "total_pages": 1},
        }


"""
Тест кейсы
-создать проект и чтобы у него были все Зконченные стадии проверять сколько в респонсе
-есть и законченные и активные
-есть только активные ???
2 - осздать различные платежи и првоерять ответы
кейс - отсутствуют этапы вообще
"""
