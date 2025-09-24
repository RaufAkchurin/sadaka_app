from app.models.referral import ReferralTypeEnum
from app.models.user import User


class TestReferralProjectLink:
    async def test_not_correct_request_param(self, auth_ac_super, auth_ac_admin, referral_dao, query_counter):
        response = await auth_ac_super.client.get(
            "/app/v1/referral/generate_link?" "ref_type=project" "&fund_id=1", cookies=auth_ac_super.cookies.dict()
        )
        assert response.status_code == 422
        assert response.json().get("detail") == "Для PROJECT нужен project_id"

        all_referrals = await referral_dao.count()
        assert all_referrals == 0

    async def test_not_exist_instance_id(self, auth_ac_super, auth_ac_admin, referral_dao, query_counter):
        response = await auth_ac_super.client.get(
            "/app/v1/referral/generate_link?" "ref_type=fund" "&project_id=99", cookies=auth_ac_super.cookies.dict()
        )
        assert response.status_code == 422
        assert response.json().get("detail") == "Нет сущности с данным project_id."

        all_referrals = await referral_dao.count()
        assert all_referrals == 0

    async def test_generate_ref_project_200(
        self, ac, auth_ac_super, auth_ac_admin, referral_dao, user_dao, query_counter, session
    ):
        # CHECK 200 status
        response = await auth_ac_super.client.get(
            "/app/v1/referral/generate_link?" "ref_type=project" "&project_id=1", cookies=auth_ac_super.cookies.dict()
        )
        assert response.status_code == 200
        assert "/v1/projects/detail/1?ref=" in response.json()
        self.ref_link = response.json()

        # CHECK queries
        assert len(query_counter) <= 10, f"Слишком много SQL-запросов: {len(query_counter)}"

        # CHECK new instance exist
        all_referrals = await referral_dao.count()
        assert all_referrals == 1

        referrals = await referral_dao.find_all()
        last_referral = referrals[-1]

        assert last_referral.type == ReferralTypeEnum.PROJECT.value
        assert last_referral.sharer_id == 1

        # CHECK response from referral_link with NEW USER (current_user)
        ref_link_response = await auth_ac_admin.client.get(self.ref_link, cookies=auth_ac_admin.cookies.dict())
        assert ref_link_response.status_code == 200
        assert ref_link_response.json() == {
            "active_stage_number": 2,
            "collected_percentage": 20,
            "description": "desc1",
            "documents": [
                {
                    "id": 1,
                    "mime": "PDF",
                    "name": "Док1 для Проекта 1",
                    "size": 123,
                    "type": "DOCUMENT",
                    "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F1.png",
                },
                {
                    "id": 2,
                    "mime": "PDF",
                    "name": "Док2 для Проекта 1",
                    "size": 123,
                    "type": "DOCUMENT",
                    "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F2.png",
                },
            ],
            "fund": {"id": 1, "name": "fund1", "picture_url": None},
            "goal": 10000,
            "id": 1,
            "name": "project1",
            "pictures_list": [],
            "region": {
                "name": "Tatarstan",
                "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F4.png",
            },
            "stages": [
                {
                    "collected": 2000,
                    "goal": 4000,
                    "name": "proj1 stage1",
                    "number": 1,
                    "reports": [
                        {
                            "id": 5,
                            "mime": "PDF",
                            "name": "Реп1 для Стадии 1",
                            "size": 123,
                            "type": "REPORT",
                            "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F5.png",
                        },
                        {
                            "id": 6,
                            "mime": "PDF",
                            "name": "Реп2 для Стадии 1",
                            "size": 123,
                            "type": "REPORT",
                            "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F6.png",
                        },
                    ],
                    "status": "finished",
                },
                {
                    "collected": 3000,
                    "goal": 5000,
                    "name": "proj1 stage2",
                    "number": 2,
                    "reports": [
                        {
                            "id": 7,
                            "mime": "PDF",
                            "name": "Реп1 для Стадии 2",
                            "size": 123,
                            "type": "REPORT",
                            "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F7.png",
                        },
                        {
                            "id": 8,
                            "mime": "PDF",
                            "name": "Реп2 для Стадии 2",
                            "size": 123,
                            "type": "REPORT",
                            "url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F8.png",
                        },
                    ],
                    "status": "active",
                },
            ],
            "status": "active",
            "total_income": 2000,
            "unique_sponsors": 1,
        }

        # CHECK referees updated referral_uses and referees
        user_admin: User = await user_dao.get_user_with_referrals_by_email(user_email="admin@test.com")
        assert len(user_admin.referral_uses) == 1
        assert user_admin.referral_uses[0] == last_referral

        await session.refresh(last_referral)
        referral_updated = await referral_dao.find_one_or_none_by_id(data_id=last_referral.id)
        assert referral_updated.referees is not None
        assert referral_updated.referees[-1].id == user_admin.id
