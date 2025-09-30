class TestRatingAPI:
    async def test_regions(self, auth_ac_super, payment_dao, query_counter) -> None:
        response = await auth_ac_super.client.get("/app/v1/ratings/regions_all", cookies=auth_ac_super.cookies.dict())

        assert response.status_code == 200
        assert response.json() is not None

        assert len(query_counter) <= 6, f"Слишком много SQL-запросов: {len(query_counter)}"

        data = response.json()

        assert data == {
            "items": [
                {
                    "id": 2,
                    "name": "Bashkortostan",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F5.png",
                    "total_income": 7000.0,
                },
                {
                    "id": 1,
                    "name": "Tatarstan",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F4.png",
                    "total_income": 2000.0,
                },
                {
                    "id": 3,
                    "name": "Aktobe obl",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F6.png",
                    "total_income": 0.0,
                },
            ],
            "state": {"page": 1, "size": 5, "total_items": 3, "total_pages": 1},
        }

    async def test_projects(self, auth_ac_super, payment_dao, query_counter, comment_dao) -> None:
        response = await auth_ac_super.client.get("/app/v1/ratings/projects", cookies=auth_ac_super.cookies.dict())

        assert response.status_code == 200
        assert response.json() is not None

        assert len(query_counter) <= 16, f"Слишком много SQL-запросов: {len(query_counter)}"

        data = response.json()

        assert data == {
            "items": [
                {
                    "count_comments": 3,
                    "fund_name": "fund3",
                    "id": 3,
                    "name": "project3",
                    "picture_url": None,
                    "status": "active",
                    "total_income": 4000,
                    "unique_sponsors": 1,
                },
                {
                    "count_comments": 2,
                    "fund_name": "fund2",
                    "id": 2,
                    "name": "project2",
                    "picture_url": None,
                    "status": "active",
                    "total_income": 3000,
                    "unique_sponsors": 1,
                },
                {
                    "count_comments": 1,
                    "fund_name": "fund1",
                    "id": 1,
                    "name": "project1",
                    "picture_url": None,
                    "status": "active",
                    "total_income": 2000,
                    "unique_sponsors": 1,
                },
                {
                    "count_comments": 0,
                    "fund_name": "fund1",
                    "id": 4,
                    "name": "project4",
                    "picture_url": None,
                    "status": "active",
                    "total_income": 0,
                    "unique_sponsors": 0,
                },
                {
                    "count_comments": 0,
                    "fund_name": "fund2",
                    "id": 5,
                    "name": "project5",
                    "picture_url": None,
                    "status": "active",
                    "total_income": 0,
                    "unique_sponsors": 0,
                },
            ],
            "state": {"page": 1, "size": 5, "total_items": 30, "total_pages": 6},
        }
