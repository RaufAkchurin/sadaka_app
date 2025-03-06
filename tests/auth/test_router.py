import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app),
                           base_url="http://test/") as client:
        response = await client.get("/")

        assert response.status_code == 200
        assert response.json() == {'author': 'Яковенко Алексей', 'community': 'https://t.me/PythonPathMaster',
                            'message': "Добро пожаловать! Проект создан для сообщества 'Легкий путь в Python'."}

@pytest.mark.asyncio
async def test_me_400():
    async with AsyncClient(transport=ASGITransport(app),
                           base_url="http://test/auth",
                           ) as client:
        response = await client.get("/me/")
        assert response.status_code == 400
        assert response.json() == {'detail': 'Токен отсутствует в заголовке'}