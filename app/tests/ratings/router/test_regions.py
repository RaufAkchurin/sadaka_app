import datetime
import uuid

from app.tests.conftest import DaoSchemas
from app.tests.schemas import TestCityAddSchema, TestPaymentAddSchema, TestRegionAddSchema, TestUserAddSchema


class TestRatingsAllAPI:
    async def test_400_authorization(self, ac) -> None:
        response = await ac.get("/app/v1/ratings/regions_all")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    async def test_200(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.get("/app/v1/ratings/regions_all", cookies=auth_ac_super.cookies.dict())
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
            user = await dao.user.add(
                TestUserAddSchema(
                    id=city_num,
                    name=f"user from city {city_num}",
                    email=f"user{city_num}@gmail.com",
                    password="12345",
                    city_id=city.id,
                )
            )

            # создаем 30 платежей от каждого пользователя
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

    async def test_regions(self, auth_ac_super) -> None:
        response = await auth_ac_super.client.get("/app/v1/ratings/regions_all", cookies=auth_ac_super.cookies.dict())

        assert response.status_code == 200
        assert response.json() is not None

        data = response.json()

        assert data == {
            "items": [
                {"id": 10, "name": "region 10", "picture_url": None, "total_income": 150000.0},
                {
                    "id": 2,
                    "name": "Bashkortostan",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F5.png",
                    "total_income": 7000.0,
                },
                {
                    "id": 1,
                    "name": "Tatarstan",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F4.png",
                    "total_income": 2000.0,
                },
                {
                    "id": 3,
                    "name": "Aktobe obl",
                    "picture_url": "https://b35fabb0-4ffa-4a15-9f0b-c3e80016c729.selstorage.ru/tests%2Fdigits%2F6.png",
                    "total_income": 0.0,
                },
            ],
            "state": {"page": 1, "size": 5, "total_items": 4, "total_pages": 1},
        }
