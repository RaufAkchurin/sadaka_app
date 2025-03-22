import pytest
from unittest.mock import patch, MagicMock
from app.auth.google.service import google_auth_service
from app.auth.google.schemas import GoogleUserData

@pytest.fixture
def mock_get_user_info():
    with patch('app.client.google.get_user_info') as mock:
        yield mock

@pytest.fixture
def mock_requests_post():
    with patch('requests.post') as mock:
        yield mock

@pytest.fixture
def mock_requests_get():
    with patch('requests.get') as mock:
        yield mock

class TestGoogleAuthService:

    @patch('requests.post')
    async def test_google_auth_service(self, mock_requests_post, mock_requests_get, mock_get_user_info, session, user_dao):
        assert await user_dao.count() == 5
        # Мокаем response от requests.post (для получения access_token)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_access_token'
        }
        mock_requests_post.return_value = mock_response

        # Мокаем response от requests.get (для получения данных пользователя)
        mock_user_info_response = MagicMock()
        mock_user_info_response.status_code = 200
        mock_user_info_response.json.return_value = {
            'name': 'test_user',
            'email': 'test@example.com',
            'picture': 'https://www.testpicture.ru/test'
        }
        mock_requests_get.return_value = mock_user_info_response

        # Мокаем get_user_info, чтобы возвращала нужные данные
        mock_get_user_info.return_value = GoogleUserData(
            name='test_user',
            email='test@example.com',
            google_access_token='test_access_token',
            picture='https://www.testpicture.ru/test'
        )

        # Вызываем функцию google_auth_service
        res = await google_auth_service(
            code='4/0AQSTgQERCWY2JwjFlIXv56vTwtVQO6NGdyIZ2J4j4tKAhzkdyAdGAxxJ-8RZIGvIrstTHQ',
            session=session
        )

        # Проверяем, что возвращенные данные соответствуют ожиданиям
        assert res.name == 'test_user'
        assert res.email == 'test@example.com'
        assert res.google_access_token == 'test_access_token'
        assert res.picture == 'https://www.testpicture.ru/test'

        # Проверяем, что запросы к API Google были вызваны
        mock_requests_post.assert_called_once()
        mock_requests_get.assert_called_once()
        assert await user_dao.count() == 6

        #TODO почему не мокается гет_юзер_инфо
        # mock_get_user_info.assert_called_once()
