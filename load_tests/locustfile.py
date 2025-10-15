import os
from typing import Any, Optional

from locust import HttpUser, SequentialTaskSet, between, task


def _ensure_leading_slash(path: str) -> str:
    return path if path.startswith("/") else f"/{path}"


SADAKA_BASE_URL = os.getenv("SADAKA_BASE_URL", "https://sadaka.pro")
SADAKA_RATING_ENDPOINT = _ensure_leading_slash(
    os.getenv("SADAKA_RATING_ENDPOINT", "/app/v1/ratings/total_info")
)

_project_status_default = os.getenv("SADAKA_PROJECT_STATUS", "active").lower()
_allowed_project_statuses = {"active", "finished", "all"}
if _project_status_default not in _allowed_project_statuses:
    raise ValueError(
        f"SADAKA_PROJECT_STATUS должен быть одним из {_allowed_project_statuses}, получено"
        f" '{_project_status_default}'."
    )

SADAKA_PROJECT_STATUS = _project_status_default
SADAKA_PROJECTS_PAGE = int(os.getenv("SADAKA_PROJECTS_PAGE", "1"))
SADAKA_PROJECTS_LIMIT = int(os.getenv("SADAKA_PROJECTS_LIMIT", "5"))


class SadakaAnonymousFlow(SequentialTaskSet):
    """
    Нагрузочный сценарий:
    1. POST /app/v1/auth/login_anonymous/ — создаём анонимного пользователя и получаем куки.
    2. GET <SADAKA_RATING_ENDPOINT> — обращаемся к выбранному рейтинговому эндпоинту.
    3. GET /app/v1/projects/all/<status> — получаем список проектов.
    """

    @task
    def anonymous_user_journey(self) -> None:
        self._reset_session_state()

        if not self._login_anonymous():
            return

        self._fetch_rating()
        self._fetch_projects()

    def _reset_session_state(self) -> None:
        self.client.cookies.clear()

    def _login_anonymous(self) -> bool:
        with self.client.post(
            "/app/v1/auth/login_anonymous/",
            name="POST /app/v1/auth/login_anonymous/",
            json={},
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"anonymous login failed ({response.status_code}): {response.text}")
                return False
            response.success()
            return True

    def _fetch_rating(self) -> bool:
        with self.client.get(
            SADAKA_RATING_ENDPOINT,
            name=f"GET {SADAKA_RATING_ENDPOINT}",
            catch_response=True,
        ) as response:
            data = self._json_or_none(response)
            if response.status_code != 200 or data is None:
                response.failure(f"rating request failed ({response.status_code}): {response.text}")
                return False
            response.success()
            return True

    def _fetch_projects(self) -> bool:
        path = f"/app/v1/projects/all/{SADAKA_PROJECT_STATUS}"
        params = {"page": SADAKA_PROJECTS_PAGE, "limit": SADAKA_PROJECTS_LIMIT}
        with self.client.get(
            path,
            params=params,
            name=f"GET {path}",
            catch_response=True,
        ) as response:
            data = self._json_or_none(response)
            if response.status_code != 200 or data is None:
                response.failure(f"projects request failed ({response.status_code}): {response.text}")
                return False

            if not isinstance(data, dict) or "items" not in data:
                response.failure("projects request failed: поле 'items' отсутствует в ответе")
                return False

            response.success()
            return True

    @staticmethod
    def _json_or_none(response: Any) -> Optional[dict]:
        try:
            return response.json()
        except ValueError:
            return None


class SadakaApiUser(HttpUser):
    host = SADAKA_BASE_URL
    wait_time = between(1, 3)
    tasks = [SadakaAnonymousFlow]
