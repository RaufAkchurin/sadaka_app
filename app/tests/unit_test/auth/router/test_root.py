from httpx import AsyncClient, ASGITransport
from app.main import app


async def test_root(async_client):
        response = await async_client.get("/")
        assert response.status_code == 200
        assert response.json() == {'author': 'Яковенко Алексей', 'community': 'https://t.me/PythonPathMaster',
                            'message': "Добро пожаловать! Проект создан для сообщества 'Легкий путь в Python'."}