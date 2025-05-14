class TestProjectList:
    async def test_400_authorization(self, ac) -> None:
        response = await ac.get("/projects/all/active")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    async def test_list_active(self, auth_ac) -> None:
        response = await auth_ac.client.get("/projects/all/active", cookies=auth_ac.cookies.dict())
        assert response.status_code == 200

        assert response.json() == [
            {
                "active_stage_number": 2,
                "fund": {"id": 2, "name": "fund2", "picture_url": None},
                "goal": 20000,
                "id": 2,
                "name": "project2",
                "payments_total": {"collected_percentage": 10, "total_collected": 2000, "unique_sponsors": 1},
                "pictures_list": [
                    "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/%D1%82%D0%B5%D1%81%D1%82%D0%BE%D0%B2%D1%8B%D0%B5%20%D0%BA%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D0%B8%2F%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-04-28%20%D0%B2%2014.39.14.png",  # noqa E501
                    "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/%D1%82%D0%B5%D1%81%D1%82%D0%BE%D0%B2%D1%8B%D0%B5%20%D0%BA%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D0%B8%2F%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-04-28%20%D0%B2%2014.39.09.png",  # noqa E501
                ],
                "status": "active",
            },
            {
                "active_stage_number": None,
                "fund": {"id": 3, "name": "fund3", "picture_url": None},
                "goal": 30000,
                "id": 3,
                "name": "project3",
                "payments_total": {"collected_percentage": 6, "total_collected": 2000, "unique_sponsors": 1},
                "pictures_list": [],
                "status": "active",
            },
        ]

    async def test_list_finished(self, auth_ac) -> None:
        response = await auth_ac.client.get("/projects/all/finished", cookies=auth_ac.cookies.dict())

        assert response.status_code == 200
        assert response.json() == [
            {
                "active_stage_number": 2,
                "fund": {"id": 1, "name": "fund1", "picture_url": None},
                "goal": 10000,
                "id": 1,
                "name": "project1",
                "payments_total": {"collected_percentage": 20, "total_collected": 2000, "unique_sponsors": 1},
                "pictures_list": [
                    "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/%D1%82%D0%B5%D1%81%D1%82%D0%BE%D0%B2%D1%8B%D0%B5%20%D0%BA%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D0%B8%2F%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-04-28%20%D0%B2%2014.38.34.png",  # noqa E501
                    "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/%D1%82%D0%B5%D1%81%D1%82%D0%BE%D0%B2%D1%8B%D0%B5%20%D0%BA%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D0%B8%2F%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-04-28%20%D0%B2%2014.38.39.png",  # noqa E501
                ],
                "status": "finished",
            }
        ]


"""
Тест кейсы
-создать проект и чтобы у него были все Зконченные стадии проверять сколько в респонсе
-есть и законченные и активные
-есть только активные ???
2 - осздать различные платежи и првоерять ответы
кейс - отсутствуют этапы вообще
"""
