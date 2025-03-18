from dataclasses import dataclass
from typing import Dict

import requests

from app.settings import Settings


@dataclass
class GoogleClient:
    settings = Settings

    def get_user_info(self, code: str) -> Dict:
        access_token = self._get_user_access_token(code)
        user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo",
                                 headers={'Authorization': f"Bearer {access_token}"})

        return user_info.json()

    def _get_user_access_token(self, code: str) -> Dict:
        data = {
            "code": code,
            "client_id": self.settings.GOOGLE_CLIENT_ID,
            "client_secret": self.settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": self.settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        response = requests.post(self.settings.GOOGLE_TOKEN_URI, data=data)
        access_token = response.json()['access_token']
