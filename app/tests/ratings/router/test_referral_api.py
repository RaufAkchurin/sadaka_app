import asyncio
import datetime
import time
import uuid

import pytest
from loguru import logger

from app.models.referral import Referral, ReferralTypeEnum
from app.tests.ratings.router.schemas import TestPaymentAddSchema
from app.v1.referrals.router import ReferralAddSchema


class TestReferralsRatingAPI:
    async def test_200(self, auth_ac_super, referral_dao) -> None:
        response = await auth_ac_super.client.get("/app/v1/ratings/referrals", cookies=auth_ac_super.cookies.dict())
        assert response.status_code == 200

    async def test_endpoint(self, auth_ac_super, referral_dao, payment_dao, session) -> None:
        now = datetime.datetime.now()

        referral_1: Referral = await referral_dao.add(ReferralAddSchema(type=ReferralTypeEnum.JOIN, sharer_id=1))

        for income_amount in [100, 200, 300]:
            uuid_num = uuid.uuid4()
            await payment_dao.add(
                TestPaymentAddSchema(
                    id=uuid_num,
                    project_id=2,
                    user_id=1,
                    income_amount=income_amount,
                    referral_id=referral_1.id,
                    stage_id=1,
                    created_at=now,
                    updated_at=now,
                    captured_at=now,
                )
            )

        referral_2: Referral = await referral_dao.add(ReferralAddSchema(type=ReferralTypeEnum.JOIN, sharer_id=2))

        for income_amount in [200, 400, 600]:
            uuid_num = uuid.uuid4()
            await payment_dao.add(
                TestPaymentAddSchema(
                    id=uuid_num,
                    project_id=2,
                    user_id=2,
                    income_amount=income_amount,
                    referral_id=referral_2.id,
                    stage_id=1,
                    created_at=now,
                    updated_at=now,
                    captured_at=now,
                )
            )

            await session.commit()

        response = await auth_ac_super.client.get("/app/v1/ratings/referrals", cookies=auth_ac_super.cookies.dict())
        assert response.status_code == 200
        assert response.json().get("items") == [
            {
                "id": 2,
                "name": "admin",
                "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F0.png",
                "total_income": 1200.0,
            },
            {
                "id": 1,
                "name": "superadmin",
                "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F9.png",
                "total_income": 600.0,
            },
            {
                "id": 3,
                "name": "moderator",
                "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F1.png",
                "total_income": 0.0,
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
        ]

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(300, 180, 250)])
    async def test_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
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

        # необязательная проверка минимального порога
        assert rps > expected_rps

        # необязательная проверка максимального порога
        assert rps < max_rps
