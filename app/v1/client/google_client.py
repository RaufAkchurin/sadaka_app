import requests

from app.settings import settings
from app.v1.auth_google.schemas import GoogleUserDataSchema


class GoogleClient:
    def get_google_user_info(self, code: str) -> GoogleUserDataSchema:
        access_token = self._get_google_user_access_token(code)
        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return GoogleUserDataSchema(**user_info.json(), google_access_token=access_token)

    @staticmethod
    def _get_google_user_access_token(code: str) -> str | None:
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_CALLBACK_URI,
            "grant_type": "authorization_code",
        }
        response = requests.post("https://accounts.google.com/o/oauth2/token", data=data)
        if response.status_code == 200:
            access_token = response.json()["access_token"]
            return access_token


google_client = GoogleClient()
