import requests

from app.auth.google.schemas import GoogleUserData
from app.settings import settings


def get_user_info( code: str) -> GoogleUserData:
    access_token = _get_user_access_token(code)
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo",
                             headers={'Authorization': f"Bearer {access_token}"})
    return GoogleUserData(**user_info.json(), google_access_token=access_token)


def _get_user_access_token( code: str) -> str:
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post(settings.GOOGLE_TOKEN_URI, data=data)
    access_token = response.json()['access_token']
    return access_token

def get_google_redirect_url() -> str:
    return settings.google_redirect_url
