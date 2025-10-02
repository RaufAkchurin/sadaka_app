import asyncio
import datetime
import time
import uuid

import pytest
from loguru import logger

from app.tests.schemas import TestCityAddSchema, TestPaymentAddSchema, TestRegionAddSchema, TestUserAddSchema


class TestDonorsAPI:
    async def test_400_authorization(self, ac) -> None:
        response = await ac.get("/app/v1/ratings/donors")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    async def test_200(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.get("/app/v1/ratings/donors", cookies=auth_ac_super.cookies.dict())
        assert response.status_code == 200

    async def test_data(self, session, payment_dao, region_dao, city_dao, user_dao):
        now = datetime.datetime.now()

        # создаем регион
        region_10 = await region_dao.add(
            TestRegionAddSchema(
                id=10,
                name="region 10",
                country_id=2,
            )
        )

        for city_num in range(10, 15):
            # создаем город
            city = await city_dao.add(
                TestCityAddSchema(
                    id=city_num,
                    name=f"city {city_num}",
                    region_id=region_10.id,
                )
            )

            # создаем пользователя для города
            user = await user_dao.add(
                TestUserAddSchema(
                    id=city_num,
                    name=f"user from city {city_num}",
                    email=f"user{city_num}@gmail.com",
                    password="12345",
                    city_id=city.id,
                )
            )

            # создаем 30 платежей от пользователя
            for _ in range(30):
                await payment_dao.add(
                    TestPaymentAddSchema(
                        id=uuid.uuid4(),
                        project_id=1,
                        user_id=user.id,
                        income_amount=1000,
                        stage_id=1,
                        created_at=now,
                        updated_at=now,
                        captured_at=now,
                    )
                )

        await session.commit()

    async def test_donors(self, auth_ac_super, payment_dao, query_counter) -> None:
        response = await auth_ac_super.client.get(
            "/app/v1/ratings/donors?page=1&limit=15",  # see your limit is 15, NOT 5)
            cookies=auth_ac_super.cookies.dict(),
        )

        assert response.status_code == 200
        assert response.json() is not None

        assert len(query_counter) <= 6, f"Слишком много SQL-запросов: {len(query_counter)}"

        data = response.json()

        assert data == {
            "items": [
                {"id": 10, "name": "user from city 10", "picture_url": None, "total_income": 30000.0},
                {"id": 11, "name": "user from city 11", "picture_url": None, "total_income": 30000.0},
                {"id": 12, "name": "user from city 12", "picture_url": None, "total_income": 30000.0},
                {"id": 13, "name": "user from city 13", "picture_url": None, "total_income": 30000.0},
                {"id": 14, "name": "user from city 14", "picture_url": None, "total_income": 30000.0},
                {
                    "id": 3,
                    "name": "moderator",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F1.png",
                    "total_income": 4000.0,
                },
                {
                    "id": 2,
                    "name": "admin",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F0.png",
                    "total_income": 3000.0,
                },
                {
                    "id": 1,
                    "name": "superadmin",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F9.png",
                    "total_income": 2000.0,
                },
                {
                    "id": 4,
                    "name": "user1",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F2.png",
                    "total_income": 0.0,
                },
                {
                    "id": 5,
                    "name": "user2",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F3.png",
                    "total_income": 0.0,
                },
            ],
            "state": {"page": 1, "size": 15, "total_items": 10, "total_pages": 1},
        }

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(200, 120, 170)])
    async def test_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
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

        # необязательная проверка минимального порога
        assert rps > expected_rps

        # необязательная проверка максимального порога
        assert rps < max_rps
