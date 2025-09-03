from app.v1.rating.router import RatingTypeEnum


class TestRatingAPI:
    async def test_400_authorization(self, ac) -> None:
        response = await ac.get(f"/app/v1/ratings/{RatingTypeEnum.DONORS.value}")
        assert response.status_code == 400
        assert response.json() == {"detail": "Токен отсутствует в заголовке"}

    async def test_200(self, auth_ac) -> None:
        response = await auth_ac.client.get(
            f"/app/v1/ratings/{RatingTypeEnum.DONORS.value}", cookies=auth_ac.cookies.dict()
        )
        assert response.status_code == 200

    async def test_donor_listing(self, auth_ac, payment_dao) -> None:
        response = await auth_ac.client.get(
            f"/app/v1/ratings/{RatingTypeEnum.DONORS.value}", cookies=auth_ac.cookies.dict()
        )
        assert response.status_code == 200
        assert response.json() is not None
