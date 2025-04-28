import asyncio
import json
import os

from sqlalchemy import insert

from app.dao.database import Base, async_session_maker, engine

# Мапа: имя модели в JSON → (модель SQLAlchemy, имя файла без расширения)
from app.file.models import File
from app.fund.models import Fund
from app.geo.models import City, Country, Region
from app.payments.models import Payment
from app.project.models import Project, Stage
from app.settings import settings
from app.users.models import User

MODELS_MAP = {
    "country": Country,
    "region": Region,
    "city": City,
    "user": User,
    # "role": Role,
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


async def prepare_database_core(session):
    try:
        # Очистка и пересоздание таблиц
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        async with async_session_maker() as session:
            for model_name, model_class in MODELS_MAP.items():
                try:
                    data = open_mock_json(model_name)
                    if not data:
                        continue
                    stmt = insert(model_class).values(data)
                    await session.execute(stmt)
                except Exception as e:
                    print(f"❌ Ошибка при вставке данных для '{model_name}': {e}")
                    raise

            await session.commit()
    except Exception as e:
        await session.rollback()
        print(f"‼️ Общая ошибка в prepare_database_core: {e}")
        raise
    finally:
        await session.close()


if __name__ == "__main__":

    async def main():
        async with async_session_maker() as session:
            assert settings.MODE == "DEV"
            await prepare_database_core(session)

    asyncio.run(main())
