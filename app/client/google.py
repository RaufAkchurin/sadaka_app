from dataclasses import dataclass
from typing import Dict
import requests

from app.auth.schemas import GoogleUserData
from app.settings import settings


@dataclass
class GoogleClient:
    settings = settings

    def get_user_info(self, code: str) -> GoogleUserData:
        access_token = self._get_user_access_token(code)
        user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo",
                                 headers={'Authorization': f"Bearer {access_token}"})
        return GoogleUserData(**user_info.json(), access_token=access_token)

    def google_auth(self, code: str):
        user_data = self.get_user_info(code)
        return user_data

    def _get_user_access_token(self, code: str) -> str:
        data = {
            "code": code,
            "client_id": self.settings.GOOGLE_CLIENT_ID,
            "client_secret": self.settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": self.settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        response = requests.post(settings.GOOGLE_TOKEN_URI, data=data)
        access_token = response.json()['access_token']
        return access_token

    def get_google_redirect_url(self) -> str:
        return self.settings.google_redirect_url
