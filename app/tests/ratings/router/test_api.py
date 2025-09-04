import asyncio
import time

import pytest
from loguru import logger

from app.v1.rating.router import RatingTypeEnum


class TestRatingAPI:
    async def test_400_authorization(self, ac) -> None:
        response = await ac.get(f"/app/v1/ratings/{RatingTypeEnum.DONORS.value}")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    async def test_200(self, auth_ac) -> None:
        response = await auth_ac.client.get(
            f"/app/v1/ratings/{RatingTypeEnum.DONORS.value}", cookies=auth_ac.cookies.dict()
        )
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
        assert data["total_income"] == 90.0

    async def test_donors(self, auth_ac, payment_dao, query_counter) -> None:
        response = await auth_ac.client.get("/app/v1/ratings/donors", cookies=auth_ac.cookies.dict())

        assert response.status_code == 200
        assert response.json() is not None

        assert len(query_counter) <= 4, f"Слишком много SQL-запросов: {len(query_counter)}"

        data = response.json()

        assert data == {
            "items": [
                {"name": "moderator", "total_income": 40.0},
                {"name": "admin", "total_income": 30.0},
                {"name": "superadmin", "total_income": 20.0},
                {"name": "user1", "total_income": 0.0},
                {"name": "user2", "total_income": 0.0},
            ],
            "state": {"page": 1, "size": 5, "total_items": 5, "total_pages": 1},
        }
