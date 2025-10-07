import asyncio
import datetime
import random
import time
import uuid

import pytest
from loguru import logger

from app.tests.conftest import DaoSchemas
from app.tests.schemas import (
    TestCityAddSchema,
    TestCommentAddSchema,
    TestPaymentAddSchema,
    TestProjectAddSchema,
    TestRegionAddSchema,
    TestUserAddSchema,
)
from app.v1.project.enums import ProjectStatusEnum


class TestProjectsAPI:
    async def test_400_authorization(self, ac) -> None:
        response = await ac.get("/app/v1/ratings/projects")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    async def test_200(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.get("/app/v1/ratings/projects", cookies=auth_ac_super.cookies.dict())
        assert response.status_code == 200

    async def test_prepare_users(self, session, dao: DaoSchemas):
        assert await dao.user.count() == 5
        # создаем регион
        region_10 = await dao.region.add(
            TestRegionAddSchema(
                id=10,
                name="region 10",
                country_id=2,
            )
        )

        # города для пользователей
        for city_num in range(10, 15):
            # создаем город
            city = await dao.city.add(
                TestCityAddSchema(
                    id=city_num,
                    name=f"city {city_num}",
                    region_id=region_10.id,
                )
            )

            # создаем пользователя для города
            await dao.user.add(
                TestUserAddSchema(
                    id=city_num,
                    name=f"user from city {city_num}",
                    email=f"user{city_num}@gmail.com",
                    password="12345",
                    city_id=city.id,
                )
            )

        await session.commit()
        assert await dao.user.count() == 10

    async def test_prepare_projects(self, session, dao: DaoSchemas):
        # перед созданием сверяемся
        assert await dao.project.count() == 30

        # создаем проекты
        for project_num in range(100, 110):
            await dao.project.add(
                TestProjectAddSchema(
                    id=project_num,
                    name=f"project{project_num}",
                    fund_id=project_num,
                    status=ProjectStatusEnum.ACTIVE,
                    description=f"description for project{project_num}",
                    goal=10000,
                )
            )
            await session.commit()

        assert await dao.project.count() == 40

    async def test_prepare_comments(self, session, dao: DaoSchemas):
        assert await dao.comment.count() == 6

        project_ids = [num for num in range(100, 110)]
        user_ids = [num for num in range(10, 15)]

        for project_id in project_ids:
            for user_id in user_ids:
                for _ in range(3):
                    await dao.comment.add(
                        TestCommentAddSchema(
                            project_id=project_id,
                            user_id=user_id,
                            content=f"comment for project {project_id} and user {user_id}",
                        )
                    )
        await session.commit()

        assert await dao.comment.count() == 156

    async def test_prepare_payments(self, session, payment_dao):
        now = datetime.datetime.now()
        project_ids = [num for num in range(100, 110)]
        user_ids = [num for num in range(10, 15)]

        # Всего 48 тысяч на каждый проект

        for project_id in project_ids:
            # создаем 30 платежей от каждого пользователя
            for _ in range(30):
                await payment_dao.add(
                    TestPaymentAddSchema(
                        provider_payment_id=str(uuid.uuid4()),
                        project_id=project_id,
                        user_id=random.choice(user_ids),
                        income_amount=1000,
                        stage_id=1,
                        created_at=now,
                        updated_at=now,
                        captured_at=now,
                    )
                )

            for _ in range(30):
                await payment_dao.add(
                    TestPaymentAddSchema(
                        provider_payment_id=str(uuid.uuid4()),
                        project_id=project_id,
                        user_id=random.choice(user_ids),
                        income_amount=500,
                        stage_id=1,
                        created_at=now,
                        updated_at=now,
                        captured_at=now,
                    )
                )

            for _ in range(30):
                await payment_dao.add(
                    TestPaymentAddSchema(
                        provider_payment_id=str(uuid.uuid4()),
                        project_id=project_id,
                        user_id=random.choice(user_ids),
                        income_amount=100,
                        stage_id=1,
                        created_at=now,
                        updated_at=now,
                        captured_at=now,
                    )
                )
        await session.commit()

    async def test_projects(self, auth_ac_super, payment_dao, query_counter, comment_dao) -> None:
        response = await auth_ac_super.client.get(
            "/app/v1/ratings/projects?page=1&limit=10", cookies=auth_ac_super.cookies.dict()
        )

        assert response.status_code == 200
        assert response.json() is not None

        data = response.json()

        assert data == {
            "items": [
                {
                    "count_comments": 15,
                    "fund_name": "Без фонда",
                    "id": 100,
                    "name": "project100",
                    "picture_url": None,
                    "status": "active",
                    "total_income": 48000.0,
                    "unique_sponsors": 5,
                },
                {
                    "count_comments": 15,
                    "fund_name": "Без фонда",
                    "id": 101,
                    "name": "project101",
                    "picture_url": None,
                    "status": "active",
                    "total_income": 48000.0,
                    "unique_sponsors": 5,
                },
                {
                    "count_comments": 15,
                    "fund_name": "Без фонда",
                    "id": 102,
                    "name": "project102",
                    "picture_url": None,
                    "status": "active",
                    "total_income": 48000.0,
                    "unique_sponsors": 5,
                },
                {
                    "count_comments": 15,
                    "fund_name": "Без фонда",
                    "id": 103,
                    "name": "project103",
                    "picture_url": None,
                    "status": "active",
                    "total_income": 48000.0,
                    "unique_sponsors": 5,
                },
                {
                    "count_comments": 15,
                    "fund_name": "Без фонда",
                    "id": 104,
                    "name": "project104",
                    "picture_url": None,
                    "status": "active",
                    "total_income": 48000.0,
                    "unique_sponsors": 5,
                },
                {
                    "count_comments": 15,
                    "fund_name": "Без фонда",
                    "id": 105,
                    "name": "project105",
                    "picture_url": None,
                    "status": "active",
                    "total_income": 48000.0,
                    "unique_sponsors": 5,
                },
                {
                    "count_comments": 15,
                    "fund_name": "Без фонда",
                    "id": 106,
                    "name": "project106",
                    "picture_url": None,
                    "status": "active",
                    "total_income": 48000.0,
                    "unique_sponsors": 5,
                },
                {
                    "count_comments": 15,
                    "fund_name": "Без фонда",
                    "id": 107,
                    "name": "project107",
                    "picture_url": None,
                    "status": "active",
                    "total_income": 48000.0,
                    "unique_sponsors": 5,
                },
                {
                    "count_comments": 15,
                    "fund_name": "Без фонда",
                    "id": 108,
                    "name": "project108",
                    "picture_url": None,
                    "status": "active",
                    "total_income": 48000.0,
                    "unique_sponsors": 5,
                },
                {
                    "count_comments": 15,
                    "fund_name": "Без фонда",
                    "id": 109,
                    "name": "project109",
                    "picture_url": None,
                    "status": "active",
                    "total_income": 48000.0,
                    "unique_sponsors": 5,
                },
            ],
            "state": {"page": 1, "size": 10, "total_items": 40, "total_pages": 4},
        }

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(200, 150, 250)])
    async def test_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
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

        # необязательная проверка минимального порога
        assert rps > expected_rps

        # необязательная проверка максимального порога
        assert rps < max_rps
