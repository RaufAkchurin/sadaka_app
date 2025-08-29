import asyncio
import json
import os
import uuid
from datetime import datetime

from sqlalchemy import insert, text

from app.models.city import City
from app.models.country import Country
from app.models.file import File
from app.models.fund import Fund
from app.models.payment import Payment
from app.models.project import Project
from app.models.region import Region
from app.models.stage import Stage
from app.models.user import User

# Мапа: имя модели в JSON → (модель SQLAlchemy, имя файла без расширения)
from app.settings import settings
from app.v1.dao.database import Base, async_session_maker, engine

MODELS_MAP = {
    "country": Country,
    "region": Region,
    "city": City,
    "user": User,
    "fund": Fund,
    "project": Project,
    "stage": Stage,
    "file": File,
    "payment": Payment,
}


def open_mock_json(model_name: str):
    test_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(test_dir, f"../tests/mocks/mock_{model_name}.json")
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


import os
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # sadaka_app/


def apply_migration():
    subprocess.run("alembic upgrade head", shell=True, check=True, cwd=PROJECT_ROOT)
    print("✅ Миграции применены.")


async def prepare_database_core(session):
    try:
        # Очистка и пересоздание таблиц
        for model_name, model_class in MODELS_MAP.items():
            try:
                data = open_mock_json(model_name)
                if not data:
                    continue

                else:
                    if model_name == "payment":
                        for item in data:
                            uuid_raw = item["id"]
                            item["id"] = uuid.UUID(uuid_raw)
                            item["created_at"] = datetime.now()
                            item["captured_at"] = datetime.now()

                stmt = insert(model_class).values(data)
                await session.execute(stmt)
            except Exception as e:
                print(f"❌ Ошибка при вставке данных для '{model_name}': {e}")
                raise

        # --- ВАЖНО: синхронизируем все последовательности ---
        for table_name in MODELS_MAP.keys():
            await session.execute(
                text(
                    f"SELECT setval(pg_get_serial_sequence('{table_name}s', 'id'),"
                    f" COALESCE(MAX(id), 1)) FROM {table_name}s;")
            )
        await session.commit()
    except Exception as e:
        await session.rollback()
        print(f"‼️ Общая ошибка в prepare_database_core: {e}")
        raise


# if __name__ == "__main__":
#
#     async def main():
#         async with async_session_maker() as session:
#             assert settings.MODE == "DEV"
#             await prepare_database_core(session)
#
#     asyncio.run(main())
