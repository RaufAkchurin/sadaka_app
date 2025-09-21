import asyncio
import time

import pytest
from loguru import logger

from app.models.referral import ReferralTypeEnum
from app.models.user import User


class TestReferralFundsLink:
    async def test_not_correct_request_param(self, auth_ac_super, auth_ac_admin, referral_dao, query_counter):
        response = await auth_ac_super.client.get(
            "/app/v1/referral/generate_link?" "ref_type=fund" "&project_id=1", cookies=auth_ac_super.cookies.dict()
        )
        assert response.status_code == 422
        assert response.json().get("detail") == "Для FUND нужен fund_id"

        all_referrals = await referral_dao.count()
        assert all_referrals == 0

    async def test_not_exist_instance_id(self, auth_ac_super, auth_ac_admin, referral_dao, query_counter):
        response = await auth_ac_super.client.get(
            "/app/v1/referral/generate_link?" "ref_type=fund" "&fund_id=99", cookies=auth_ac_super.cookies.dict()
        )
        assert response.status_code == 422
        assert response.json().get("detail") == "Нет сущности с данным fund_id."

        all_referrals = await referral_dao.count()
        assert all_referrals == 0

    async def test_generate_ref_fund_200(
        self, ac, auth_ac_super, auth_ac_admin, referral_dao, user_dao, query_counter, session
    ):
        # CHECK 200 status
        response = await auth_ac_super.client.get(
            "/app/v1/referral/generate_link?" "ref_type=fund" "&fund_id=1", cookies=auth_ac_super.cookies.dict()
        )
        assert response.status_code == 200
        assert "app/v1/funds/detail/1?ref" in response.json()
        self.ref_link = response.json()

        # CHECK queries
        assert len(query_counter) <= 10, f"Слишком много SQL-запросов: {len(query_counter)}"

        # CHECK new instance exist
        all_referrals = await referral_dao.count()
        assert all_referrals == 1

        referrals = await referral_dao.find_all()
        last_referral = referrals[-1]

        assert last_referral.type == ReferralTypeEnum.FUND.value
        assert last_referral.sharer_id == 1

        # CHECK response from referral_link with NEW USER (current_user)
        ref_link_response = await auth_ac_admin.client.get(self.ref_link, cookies=auth_ac_admin.cookies.dict())
        assert ref_link_response.status_code == 200
        assert ref_link_response.json() == {
            "address": "address1",
            "description": "desc1",
            "documents": [
                {
                    "id": 17,
                    "mime": "JPEG",
                    "name": "Документ 1 для Фонда 1",
                    "size": 123,
                    "type": "PICTURE",
                    "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F7.png",
                },
                {
                    "id": 18,
                    "mime": "JPEG",
                    "name": "Документ 2 для Фонда 1",
                    "size": 123,
                    "type": "PICTURE",
                    "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F8.png",
                },
            ],
            "hot_line": "+79176542281",
            "id": 1,
            "name": "fund1",
            "projects": [
                {
                    "active_stage_number": 2,
                    "collected_percentage": 20,
                    "fund": {"id": 1, "name": "fund1", "picture_url": None},
                    "goal": 10000,
                    "id": 1,
                    "name": "project1",
                    "pictures_list": [],
                    "status": "active",
                    "total_income": 2000.0,
                    "unique_sponsors": 1,
                },
                {
                    "active_stage_number": None,
                    "collected_percentage": 0,
                    "fund": {"id": 1, "name": "fund1", "picture_url": None},
                    "goal": 40000,
                    "id": 4,
                    "name": "project4",
                    "pictures_list": [],
                    "status": "active",
                    "total_income": 0.0,
                    "unique_sponsors": 0,
                },
                {
                    "active_stage_number": None,
                    "collected_percentage": 0,
                    "fund": {"id": 1, "name": "fund1", "picture_url": None},
                    "goal": 70000,
                    "id": 7,
                    "name": "project7",
                    "pictures_list": [],
                    "status": "active",
                    "total_income": 0.0,
                    "unique_sponsors": 0,
                },
                {
                    "active_stage_number": None,
                    "collected_percentage": 0,
                    "fund": {"id": 1, "name": "fund1", "picture_url": None},
                    "goal": 100000,
                    "id": 10,
                    "name": "project10",
                    "pictures_list": [],
                    "status": "active",
                    "total_income": 0.0,
                    "unique_sponsors": 0,
                },
                {
                    "active_stage_number": None,
                    "collected_percentage": 0,
                    "fund": {"id": 1, "name": "fund1", "picture_url": None},
                    "goal": 130000,
                    "id": 13,
                    "name": "project13",
                    "pictures_list": [],
                    "status": "active",
                    "total_income": 0.0,
                    "unique_sponsors": 0,
                },
                {
                    "active_stage_number": None,
                    "collected_percentage": 0,
                    "fund": {"id": 1, "name": "fund1", "picture_url": None},
                    "goal": 160000,
                    "id": 16,
                    "name": "project16",
                    "pictures_list": [],
                    "status": "active",
                    "total_income": 0.0,
                    "unique_sponsors": 0,
                },
                {
                    "active_stage_number": None,
                    "collected_percentage": 0,
                    "fund": {"id": 1, "name": "fund1", "picture_url": None},
                    "goal": 190000,
                    "id": 19,
                    "name": "project19",
                    "pictures_list": [],
                    "status": "active",
                    "total_income": 0.0,
                    "unique_sponsors": 0,
                },
                {
                    "active_stage_number": None,
                    "collected_percentage": 0,
                    "fund": {"id": 1, "name": "fund1", "picture_url": None},
                    "goal": 220000,
                    "id": 22,
                    "name": "project22",
                    "pictures_list": [],
                    "status": "finished",
                    "total_income": 0.0,
                    "unique_sponsors": 0,
                },
                {
                    "active_stage_number": None,
                    "collected_percentage": 0,
                    "fund": {"id": 1, "name": "fund1", "picture_url": None},
                    "goal": 250000,
                    "id": 25,
                    "name": "project25",
                    "pictures_list": [],
                    "status": "finished",
                    "total_income": 0.0,
                    "unique_sponsors": 0,
                },
                {
                    "active_stage_number": None,
                    "collected_percentage": 0,
                    "fund": {"id": 1, "name": "fund1", "picture_url": None},
                    "goal": 280000,
                    "id": 28,
                    "name": "project28",
                    "pictures_list": [],
                    "status": "finished",
                    "total_income": 0.0,
                    "unique_sponsors": 0,
                },
            ],
            "projects_count": 10,
            "region_name": "Tatarstan",
            "total_income": 2000.0,
        }

        # CHECK referees updated referral_uses and referees
        user_admin: User = await user_dao.get_user_with_referrals_by_email(user_email="admin@test.com")
        assert len(user_admin.referral_uses) == 1
        assert user_admin.referral_uses[0] == last_referral

        await referral_dao.refresh(last_referral)
        referral_updated = await referral_dao.find_one_or_none_by_id(data_id=last_referral.id)
        assert referral_updated.referees is not None
        assert referral_updated.referees[-1].id == user_admin.id

    @pytest.mark.parametrize("num_requests, expected_rps, max_rps", [(200, 70, 120)])
    async def test_rps(self, auth_ac_super, num_requests, expected_rps, max_rps) -> None:
        async def make_request():
            response = await auth_ac_super.client.get(
                "/app/v1/referral/generate_link?" "ref_type=fund" "&fund_id=1", cookies=auth_ac_super.cookies.dict()
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
