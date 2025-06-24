import os
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent  # sadaka_app/
DB_FILE = PROJECT_ROOT / "data" / "db.sqlite3"
MIGRATIONS_DIR = PROJECT_ROOT / "app" / "migration" / "versions"
DB_FILL_SCRIPT = PROJECT_ROOT / "app" / "utils" / "scripts" / "local_db_fill.py"


def apply_migration():
    subprocess.run("alembic upgrade head", shell=True, check=True, cwd=PROJECT_ROOT)
    print("✅ Миграции применены.")


if __name__ == "__main__":
    os.chdir(PROJECT_ROOT)
    print(f"📁 Переход в корень проекта: {PROJECT_ROOT}")
    apply_migration()
