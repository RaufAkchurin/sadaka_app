import datetime
import uuid

from app.tests.conftest import DaoSchemas
from app.tests.schemas import TestCityAddSchema, TestPaymentAddSchema, TestRegionAddSchema, TestUserAddSchema


class TestTotalInfoAPI:
    async def test_400_authorization(self, ac) -> None:
        response = await ac.get("/app/v1/ratings/total_info")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    async def test_200(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.get("/app/v1/ratings/total_info", cookies=auth_ac_super.cookies.dict())
        assert response.status_code == 200

    async def test_data(self, session, dao: DaoSchemas):
        now = datetime.datetime.now()

        # создаем регион
        region_10 = await dao.region.add(
            TestRegionAddSchema(
                id=10,
                name="region 10",
                country_id=2,
            )
        )

        for city_num in range(10, 20):
            # создаем город
            city = await dao.city.add(
                TestCityAddSchema(
                    id=city_num,
                    name=f"city {city_num}",
                    region_id=region_10.id,
                )
            )

            # создаем пользователя для города
            user = await dao.user.add(
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
                await dao.payment.add(
                    TestPaymentAddSchema(
                        provider_payment_id=str(uuid.uuid4()),
                        project_id=1,
                        user_id=user.id,
                        income_amount=1000,
                        stage_id=1,
                        created_at=now,
                        updated_at=now,
                    )
                )

        await session.commit()

    async def test_total_info(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.get("/app/v1/ratings/total_info", cookies=auth_ac_super.cookies.dict())
        assert response.status_code == 200
        assert response.json() is not None

        data = response.json()
        assert data["autopayments"] == 0
        assert data["cities"] == 13
        assert data["payments"] == 306
        assert data["projects"] == 30
        assert data["total_income"] == 309000.0
