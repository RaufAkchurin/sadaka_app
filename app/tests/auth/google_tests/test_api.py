import pytest

class TestGoogle:

    async def test_login(self, ac):
        url = "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=82940823785-f0042dda793mqu66np8a9p72alrenme1.apps.googleusercontent.com&redirect_uri=http://localhost:8000/google_oauth/callback/&scope=openid%20profile%20email&access_type=offline"
        response = await ac.get("/google_oauth/login/")
        assert response.status_code == 307
        assert response.headers.get('location') == url

#TODO сделать фейк гугл клиент
#TODO эмитаця регистрации нового пользака и проверка наличия ЖВТ токенов
#TODO эмитаця логаут и проверка отсуствия токенов
