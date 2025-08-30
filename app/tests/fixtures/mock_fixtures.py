from pathlib import Path

import pytest
from sqlalchemy import insert

from app.utils.scripts.local_db_fill import MODELS_MAP, open_mock_json, prepare_database_core
from app.v1.dao.database import async_session_maker

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # sadaka_app/


# --- Универсальная фикстура для загрузки конкретного набора ---
@pytest.fixture(scope="class")
async def load_mock():
    async with async_session_maker() as session:

        async def _load_mock(model_name: str):
            if model_name not in MODELS_MAP:
                raise ValueError(f"Неизвестная модель {model_name}")

            model = MODELS_MAP[model_name]

            # Загружаем JSON
            data = open_mock_json(model_name)
            if not data:
                return []

            stmt = insert(model).values(data).returning(model)
            result = await session.execute(stmt)
            await session.commit()
            return result.unique().fetchall()

        yield _load_mock


# -----------------------------------------------------------------
# --- Автоматическая генерация фикстур вида mock_<model_name>s ---
def _make_fixture(model_name: str):
    @pytest.fixture(scope="class")
    async def _fixture(load_mock):
        return await load_mock(model_name)

    _fixture.__name__ = f"mock_{model_name}s"
    return _fixture


# НЕ УДАЛЯТЬ И НЕ ОТДЕЛЯТЬ ОТ _make_fixture
# Создаём фикстуры для всех моделей в MODELS_MAP
for model_name in MODELS_MAP.keys():
    globals()[f"mock_{model_name}s"] = _make_fixture(model_name)
# ------------------------------------------------------------------


@pytest.fixture(scope="class")
async def geo_fixture(load_mock):
    await load_mock("country")
    await load_mock("region")
    await load_mock("city")


@pytest.fixture(scope="class")
async def users_fixture(load_mock, geo_fixture):
    await load_mock("user")


@pytest.fixture(scope="class")
async def projects_fixture(load_mock, geo_fixture):
    await load_mock("fund")
    await load_mock("project")


# --- Полная загрузка всех моков (интеграционные тесты) ---
@pytest.fixture(scope="session", autouse=False)
async def prepare_all_mocks():
    """
    Загружает ВСЕ моки из MODELS_MAP.
    Использовать, когда нужно полностью заполнить БД.
    """
    async with async_session_maker() as session:
        await prepare_database_core(session)
