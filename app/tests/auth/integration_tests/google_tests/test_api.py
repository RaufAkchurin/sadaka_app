import pytest

class TestGoogle:

    async def test_login(self, ac):
        url = "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=82940823785-f0042dda793mqu66np8a9p72alrenme1.apps.googleusercontent.com&redirect_uri=http://localhost:8000/google_oauth/callback/&scope=openid%20profile%20email&access_type=offline"
        response = await ac.get("/google_oauth/login/")
        assert response.status_code == 307
        assert response.headers.get('location') == url

    async def test_redirect(self, ac):
        url = "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=82940823785-f0042dda793mqu66np8a9p72alrenme1.apps.googleusercontent.com&redirect_uri=http://localhost:8000/google_oauth/callback/&scope=openid%20profile%20email&access_type=offline"
        response = await ac.get(url)
        assert response.status_code == 200

    async def test_callback(self, ac):
        code = '4/0AQSTgQERCWY2JwjFlIXv56vTwtVQO6NGdyIZ2J4j4tKAhzkdyAdGAxxJ-8RZIGvIrstTHQ'
        response = await ac.get(f"/google_oauth/callback/?code={code}")
        assert response.status_code == 200