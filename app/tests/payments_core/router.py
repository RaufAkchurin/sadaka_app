import asyncio
import time

import pytest
from loguru import logger


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

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(100, 140, 240)])
    async def test_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get(
                "/app/v1/payments/my_donations", cookies=auth_ac_super.cookies.dict()
            )

            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        # необязательная проверка минимального порога
        assert rps > expected_rps

        # необязательная проверка максимального порога
        assert rps < max_rps
