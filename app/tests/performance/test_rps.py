import asyncio
import copy
import time
import uuid
from unittest.mock import patch

import pytest
from loguru import logger
from starlette.datastructures import Address

from app.tests.fixtures.dao import DaoSchemas
from app.tests.payments_tbank.router.test_callback import TestTbankPaymentCallback
from app.tests.payments_yookassa.router.test_callback import TestYOOKASSAPaymentCallback

pytest.skip("performance tests are disabled", allow_module_level=True)
class TestRpsPerformance:
    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(400, 300, 360)])
    async def test_city_list_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        url = "/app/v1/cities/all"
        cookies = auth_ac_super.cookies.dict()

        async def make_request():
            response = await auth_ac_super.client.get(url, cookies=cookies)
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(400, 260, 330)])
    async def test_comments_project_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get(
                "/app/v1/comments/1",
                params={"project_id": 1, "page": 1, "limit": 10},
                cookies=auth_ac_super.cookies.dict(),
            )
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(300, 45, 90)])
    async def test_funds_detail_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get("/app/v1/funds/detail/1", cookies=auth_ac_super.cookies.dict())
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(100, 100, 240)])
    async def test_payments_my_donations_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
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

        assert rps > expected_rps
        assert rps < max_rps

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(100, 140, 240)])
    async def test_payments_project_donations_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get(
                "/app/v1/payments/project_donations/1", cookies=auth_ac_super.cookies.dict()
            )
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(200, 70, 115)])
    async def test_projects_detail_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get("/app/v1/projects/detail/1", cookies=auth_ac_super.cookies.dict())
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(200, 140, 170)])
    async def test_projects_list_finished_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get(
                "/app/v1/projects/all/finished", cookies=auth_ac_super.cookies.dict()
            )
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(100, 30, 50)])
    async def test_referral_my_referral_list_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get(
                "/app/v1/referral/my_referral_list", cookies=auth_ac_super.cookies.dict()
            )
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(100, 30, 70)])
    async def test_referral_my_referral_list_db_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get(
                "/app/v1/referral/my_referral_list_DB_PAGINATION", cookies=auth_ac_super.cookies.dict()
            )
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(200, 90, 150)])
    async def test_referral_generate_link_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get(
                "/app/v1/referral/generate_link?ref_type=fund&fund_id=1", cookies=auth_ac_super.cookies.dict()
            )
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(200, 120, 170)])
    async def test_ratings_donors_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get("/app/v1/ratings/donors", cookies=auth_ac_super.cookies.dict())
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(200, 150, 250)])
    async def test_ratings_projects_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get("/app/v1/ratings/projects", cookies=auth_ac_super.cookies.dict())
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(200, 90, 170)])
    async def test_ratings_regions_all_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get(
                "/app/v1/ratings/regions_all", cookies=auth_ac_super.cookies.dict()
            )
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(400, 300, 370)])
    async def test_ratings_regions_by_project_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get(
                "/app/v1/ratings/regions/1", cookies=auth_ac_super.cookies.dict()
            )
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(300, 200, 270)])
    async def test_ratings_referrals_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get("/app/v1/ratings/referrals", cookies=auth_ac_super.cookies.dict())
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(300, 250, 320)])
    async def test_ratings_total_info_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get(
                "/app/v1/ratings/total_info", cookies=auth_ac_super.cookies.dict()
            )
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @patch("fastapi.Request.client", Address("185.71.76.1", 1234))
    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(100, 40, 70)])
    async def test_payments_yookassa_callback_rps(
        self, ac, num_requests, expected_rps, max_rps, dao: DaoSchemas
    ) -> None:
        async def make_request():
            payload = copy.deepcopy(TestYOOKASSAPaymentCallback.callback_mock_success)
            payload["id"] = str(uuid.uuid4())

            response = await ac.post("/app/v1/payments/yookassa/callback", json={"object": payload})
            assert response.status_code == 200
            return response

        tasks = [make_request() for _ in range(num_requests)]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        payments_count = await dao.payment.count()
        assert payments_count == 106

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps

    @patch("fastapi.Request.client", Address(TestTbankPaymentCallback.valid_ip, 1234))
    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(100, 40, 70)])
    async def test_payments_tbank_callback_rps(
        self, ac, num_requests, expected_rps, max_rps, dao: DaoSchemas
    ) -> None:
        unique_requests = []
        for i in range(1, num_requests + 1):
            payload = copy.deepcopy(TestTbankPaymentCallback.callback_mock_success)
            payload["PaymentId"] = str(i)
            unique_requests.append(payload)

        async def make_request(payload):
            response = await ac.post("/app/v1/payments/tbank/callback", json=payload)
            assert response.status_code == 200
            return response

        tasks = [make_request(req) for req in unique_requests]

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        payments_count = await dao.payment.count()
        assert payments_count == 107

        rps = num_requests / elapsed
        logger.info(f"⚡ {num_requests} requests in {elapsed:.2f}s → {rps:.2f} RPS")

        assert rps > expected_rps
        assert rps < max_rps
