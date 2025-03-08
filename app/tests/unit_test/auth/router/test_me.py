from httpx import AsyncClient, ASGITransport
from app.main import app


class TestAuthMeEndpoint:
    async def test_me_400(self):
        async with AsyncClient(transport=ASGITransport(app),
                               base_url="http://test/auth",
                               ) as client:
            response = await client.get("/me/")
            assert response.status_code == 400
            assert response.json() == {'detail': 'Токен отсутствует в заголовке'}