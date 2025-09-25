import asyncio
import datetime
import time
import uuid

import pytest
from loguru import logger

from app.models.referral import Referral, ReferralTypeEnum
from app.tests.ratings.router.schemas import TestPaymentAddSchema
from app.v1.referrals.router import ReferralAddSchema


class TestReferralListAPI:
    async def test_200(self, auth_ac_super, referral_dao) -> None:
        response = await auth_ac_super.client.get(
            "/app/v1/referral/referral_list", cookies=auth_ac_super.cookies.dict()
        )
        assert response.status_code == 200

    async def test_endpoint(self, auth_ac_super, referral_dao, payment_dao, session) -> None:
        now = datetime.datetime.now()

        # JOIN TYPE
        referral_1: Referral = await referral_dao.add(ReferralAddSchema(type=ReferralTypeEnum.JOIN, sharer_id=1))

        for income_amount in [100, 200, 300]:
            uuid_num = uuid.uuid4()
            await payment_dao.add(
                TestPaymentAddSchema(
                    id=uuid_num,
                    project_id=2,
                    user_id=4,
                    income_amount=income_amount,
                    referral_id=referral_1.id,
                    stage_id=1,
                    created_at=now,
                    updated_at=now,
                    captured_at=now,
                )
            )

        # FUND TYPE
        referral_2: Referral = await referral_dao.add(
            ReferralAddSchema(
                type=ReferralTypeEnum.FUND,
                sharer_id=1,
                fund_id=1,
            )
        )

        for income_amount in [200, 400, 600, 700]:
            uuid_num = uuid.uuid4()
            await payment_dao.add(
                TestPaymentAddSchema(
                    id=uuid_num,
                    project_id=2,
                    user_id=5,
                    income_amount=income_amount,
                    referral_id=referral_2.id,
                    stage_id=1,
                    created_at=now,
                    updated_at=now,
                    captured_at=now,
                )
            )

        # PROJECT TYPE
        referral_3: Referral = await referral_dao.add(
            ReferralAddSchema(
                type=ReferralTypeEnum.PROJECT,
                sharer_id=1,
                project_id=1,
            )
        )

        for income_amount in [300, 500, 700, 900, 1100]:
            uuid_num = uuid.uuid4()
            await payment_dao.add(
                TestPaymentAddSchema(
                    id=uuid_num,
                    project_id=2,
                    user_id=5,
                    income_amount=income_amount,
                    referral_id=referral_3.id,
                    stage_id=1,
                    created_at=now,
                    updated_at=now,
                    captured_at=now,
                )
            )

        await session.commit()

        response = await auth_ac_super.client.get(
            "/app/v1/referral/referral_list", cookies=auth_ac_super.cookies.dict()
        )
        assert response.status_code == 200

        assert response.json()["items"] == []

        # TODO TEST RESPONSE DATA

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(300, 170, 220)])
    async def test_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get(
                "/app/v1/referral/referral_list", cookies=auth_ac_super.cookies.dict()
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
