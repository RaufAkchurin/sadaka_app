import asyncio
import datetime
import time
import uuid

import pytest
from loguru import logger

from app.tests.schemas import TestCityAddSchema, TestPaymentAddSchema, TestRegionAddSchema, TestUserAddSchema


class TestRatingRegionPaymentsByProjectIdAPI:
    async def test_data_region_10(self, session, payment_dao, region_dao, city_dao, user_dao):
        now = datetime.datetime.now()
        region_10 = await region_dao.add(
            TestRegionAddSchema(
                id=10,
                name="region 10",
                country_id=2,
            )
        )

        city_for_10 = await city_dao.add(
            TestCityAddSchema(
                id=10,
                name="city 10",
                region_id=region_10.id,
            )
        )

        user_from_region_10 = await user_dao.add(
            TestUserAddSchema(
                id=10, name="user from city 10", email="user10@gmail.com", password="12345", city_id=city_for_10.id
            )
        )

        # Valid data for test
        for income_amount in range(100):
            uuid_num = uuid.uuid4()
            await payment_dao.add(
                TestPaymentAddSchema(
                    id=uuid_num,
                    project_id=1,
                    user_id=user_from_region_10.id,
                    income_amount=1000,
                    stage_id=1,
                    created_at=now,
                    updated_at=now,
                    captured_at=now,
                )
            )
        await session.commit()

    async def test_data_region_20_user_first(self, session, payment_dao, region_dao, city_dao, user_dao):
        now = datetime.datetime.now()
        region_20 = await region_dao.add(
            TestRegionAddSchema(
                id=20,
                name="region 20",
                country_id=2,
            )
        )

        city_for_20 = await city_dao.add(
            TestCityAddSchema(
                id=20,
                name="city 20",
                region_id=region_20.id,
            )
        )

        user_from_region_20 = await user_dao.add(
            TestUserAddSchema(
                id=21,
                name="user from city 20 first",
                email="user201@gmail.com",
                password="12345",
                city_id=city_for_20.id,
            )
        )

        # Valid data for test
        for income_amount in range(100):
            uuid_num = uuid.uuid4()
            await payment_dao.add(
                TestPaymentAddSchema(
                    id=uuid_num,
                    project_id=1,
                    user_id=user_from_region_20.id,
                    income_amount=1000,
                    stage_id=1,
                    created_at=now,
                    updated_at=now,
                    captured_at=now,
                )
            )
        await session.commit()

    async def test_data_region_20_user_second(self, session, payment_dao, region_dao, city_dao, user_dao):
        now = datetime.datetime.now()
        user_from_region_20 = await user_dao.add(
            TestUserAddSchema(
                id=22, name="user from city 20 second", email="user202@gmail.com", password="12345", city_id=20
            )
        )

        # Valid data for test
        for income_amount in range(100):
            uuid_num = uuid.uuid4()
            await payment_dao.add(
                TestPaymentAddSchema(
                    id=uuid_num,
                    project_id=1,
                    user_id=user_from_region_20.id,
                    income_amount=1000,
                    stage_id=1,
                    created_at=now,
                    updated_at=now,
                    captured_at=now,
                )
            )
        await session.commit()

    async def test_400_authorization(self, ac) -> None:
        response = await ac.get("/app/v1/ratings/regions/1")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    async def test_200(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.get("/app/v1/ratings/regions/1", cookies=auth_ac_super.cookies.dict())
        assert response.status_code == 200

    async def test_regions(self, auth_ac_super, payment_dao, query_counter) -> None:
        response = await auth_ac_super.client.get("/app/v1/ratings/regions/1", cookies=auth_ac_super.cookies.dict())

        assert response.status_code == 200
        assert response.json() is not None

        data = response.json()

        assert data == {
            "items": [
                {"id": 20, "name": "region 20", "picture_url": None, "total_income": 200000.0},
                {"id": 10, "name": "region 10", "picture_url": None, "total_income": 100000.0},
                {
                    "id": 1,
                    "name": "Tatarstan",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F4.png",
                    "total_income": 2000.0,
                },
                {
                    "id": 2,
                    "name": "Bashkortostan",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F5.png",
                    "total_income": 0.0,
                },
                {
                    "id": 3,
                    "name": "Aktobe obl",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F6.png",
                    "total_income": 0.0,
                },
            ],
            "state": {"page": 1, "size": 5, "total_items": 5, "total_pages": 1},
        }

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(400, 240, 280)])
    async def test_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get("/app/v1/ratings/regions/1", cookies=auth_ac_super.cookies.dict())

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
