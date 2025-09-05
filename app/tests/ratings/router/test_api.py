import asyncio
import time

import pytest
from loguru import logger


class TestRatingAPI:
    async def test_400_authorization(self, ac) -> None:
        response = await ac.get("/app/v1/ratings/total_info")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    async def test_200(self, auth_ac) -> None:
        response = await auth_ac.client.get("/app/v1/ratings/total_info", cookies=auth_ac.cookies.dict())
        assert response.status_code == 200

    @pytest.mark.parametrize("num_requests", [50, 100, 200])
    async def test_rps(self, auth_ac, num_requests) -> None:
        url = "/app/v1/ratings/donors"
        cookies = auth_ac.cookies.dict()

        async def make_request():
            response = await auth_ac.client.get(url, cookies=cookies)
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        # необязательная проверка минимального порога
        assert rps > 55

    async def test_total_info(self, auth_ac, payment_dao, user_dao, query_counter) -> None:
        response = await auth_ac.client.get("/app/v1/ratings/total_info", cookies=auth_ac.cookies.dict())
        assert response.status_code == 200
        assert response.json() is not None

        assert len(query_counter) <= 6, f"Слишком много SQL-запросов: {len(query_counter)}"

        data = response.json()
        assert data["autopayments"] == 0
        assert data["cities"] == 3
        assert data["payments"] == 6
        assert data["projects"] == 30
        assert data["total_income"] == 9000.0

    async def test_donors(self, auth_ac, payment_dao, query_counter) -> None:
        response = await auth_ac.client.get("/app/v1/ratings/donors", cookies=auth_ac.cookies.dict())

        assert response.status_code == 200
        assert response.json() is not None

        assert len(query_counter) <= 4, f"Слишком много SQL-запросов: {len(query_counter)}"

        data = response.json()

        assert data == {
            "items": [
                {
                    "name": "moderator",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F1.png",
                    "total_income": 4000.0,
                },
                {
                    "name": "admin",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F0.png",
                    "total_income": 3000.0,
                },
                {
                    "name": "superadmin",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F9.png",
                    "total_income": 2000.0,
                },
                {
                    "name": "user1",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F2.png",
                    "total_income": 0.0,
                },
                {
                    "name": "user2",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F3.png",
                    "total_income": 0.0,
                },
            ],
            "state": {"page": 1, "size": 5, "total_items": 5, "total_pages": 1},
        }

    async def test_regions(self, auth_ac, payment_dao, query_counter) -> None:
        response = await auth_ac.client.get("/app/v1/ratings/regions", cookies=auth_ac.cookies.dict())

        assert response.status_code == 200
        assert response.json() is not None

        assert len(query_counter) <= 4, f"Слишком много SQL-запросов: {len(query_counter)}"

        data = response.json()

        assert data == {
            "items": [
                {
                    "name": "Bashkortostan",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F5.png",
                    "total_income": 7000.0,
                },
                {
                    "name": "Tatarstan",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F4.png",
                    "total_income": 2000.0,
                },
            ],
            "state": {"page": 1, "size": 5, "total_items": 2, "total_pages": 1},
        }

    async def test_projects(self, auth_ac, payment_dao, query_counter) -> None:
        response = await auth_ac.client.get("/app/v1/ratings/projects", cookies=auth_ac.cookies.dict())

        assert response.status_code == 200
        assert response.json() is not None

        assert len(query_counter) <= 6, f"Слишком много SQL-запросов: {len(query_counter)}"

        data = response.json()

        assert data == {
            "items": [
                {
                    "active_stage_number": None,
                    "collected_percentage": 13,
                    "fund": {"id": 3, "name": "fund3", "picture_url": None},
                    "goal": 30000,
                    "id": 3,
                    "name": "project3",
                    "pictures_list": [],
                    "status": "active",
                    "total_collected": 4000,
                    "unique_sponsors": 1,
                },
                {
                    "active_stage_number": 2,
                    "collected_percentage": 15,
                    "fund": {"id": 2, "name": "fund2", "picture_url": None},
                    "goal": 20000,
                    "id": 2,
                    "name": "project2",
                    "pictures_list": [],
                    "status": "active",
                    "total_collected": 3000,
                    "unique_sponsors": 1,
                },
                {
                    "active_stage_number": 2,
                    "collected_percentage": 20,
                    "fund": {"id": 1, "name": "fund1", "picture_url": None},
                    "goal": 10000,
                    "id": 1,
                    "name": "project1",
                    "pictures_list": [],
                    "status": "active",
                    "total_collected": 2000,
                    "unique_sponsors": 1,
                },
            ],
            "state": {"page": 1, "size": 5, "total_items": 3, "total_pages": 1},
        }
