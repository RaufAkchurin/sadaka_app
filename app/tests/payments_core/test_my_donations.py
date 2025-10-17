import datetime
import uuid

from app.tests.schemas import TestPaymentAddSchema


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

class TestProjectDonations:
    async def test_project_donations(self, ac, auth_ac_super, query_counter, payment_dao, session) -> None:
        now = datetime.datetime.now()

        income_amount = 100.0

        for _ in range(500):
            income_amount += 10.0
            uuid_num = uuid.uuid4()
            await payment_dao.add(
                TestPaymentAddSchema(
                    provider_payment_id=str(uuid_num),
                    project_id=1,
                    user_id=1,
                    amount=income_amount,
                    income_amount=income_amount,
                    stage_id=1,
                    created_at=now,
                    updated_at=now,
                    referral_id=None,
                )
            )

        await session.commit()

        response = await auth_ac_super.client.get(
            "/app/v1/payments/project_donations/1", cookies=auth_ac_super.cookies.dict()
        )
        assert response.status_code == 200

        data = response.json()

        assert data is not None

        assert data["items"][0] is not None
        assert data["items"][0].get("amount") == 1100.0
        assert data["items"][0].get("donor_name") == "superadmin"
        assert data["items"][0].get("created_at") is not None

        assert data["items"][1] is not None
        assert data["items"][1].get("amount") == 1200.0
        assert data["items"][1].get("donor_name") == "superadmin"
        assert data["items"][1].get("created_at") is not None
