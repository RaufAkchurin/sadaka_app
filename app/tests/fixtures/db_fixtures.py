import subprocess
from pathlib import Path

from sqlalchemy import text

from app.v1.dao.database import engine

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent  # sadaka_app/


def apply_migration():
    result = subprocess.run(
        "alembic upgrade head",
        shell=True,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("❌ Alembic failed:")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        raise RuntimeError("Alembic migrations failed")
    print("✅ Миграции применены.")


async def reset_database():
    async with engine.begin() as conn:
        # удаляем схему public со всеми объектами
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        # создаём схему заново
        await conn.execute(text("CREATE SCHEMA public;"))

    # применяем все миграции
    apply_migration()

    # сбрасываем все соединения и prepared statements
    await engine.dispose()
