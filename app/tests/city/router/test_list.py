import asyncio
import time

import pytest
from loguru import logger


class TestCityList:
    async def test_400_authorization(self, ac) -> None:
        response = await ac.get("/app/v1/cities/all")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    @pytest.mark.parametrize("num_requests, expected_rps", [(1000, 130)])
    async def test_rps(self, auth_ac_super, num_requests, expected_rps) -> None:
        url = "/app/v1/cities/all"
        cookies = auth_ac_super.cookies.dict()

        async def make_request():
            response = await auth_ac_super.client.get(url, cookies=cookies)
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(1000)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        # необязательная проверка минимального порога
        assert rps > expected_rps

    async def test_list(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.get("/app/v1/cities/all", cookies=auth_ac_super.cookies.dict())
        assert response.status_code == 200

        assert response.json() == {
            "items": [{"id": 1, "name": "Kazan"}, {"id": 2, "name": "Ufa"}, {"id": 3, "name": "Ishim"}],
            "state": {"page": 1, "size": 5, "total_items": 3, "total_pages": 1},
        }
