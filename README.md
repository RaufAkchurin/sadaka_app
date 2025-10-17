# Sadaka App backend

Sadaka App — асинхронный backend для благотворительной платформы, объединяющий проекты, фонды и пожертвования. Приложение предоставляет REST API, административную панель и интеграции с платежными сервисами.

## Возможности
- JWT-аутентификация (логин по паролю, обновление токена, а также SMS- и Google OAuth-авторизация)
- Управление пользователями, фондами, проектами, пожертвованиями, рейтингами и комментариями
- Интеграции с YooKassa и Т-Банк для приема платежей
- Работа с реферальными ссылками и S3-совместимым хранилищем файлов
- SQLAdmin-панель для ручного управления данными
- Встроенная телеметрия: логирование SQL-запросов, профилирование и отправка ошибок в Sentry

## Аутентификация и регистрация
- **Email + пароль**: классическая регистрация с хранением пароля в хешированном виде (bcrypt) и выдачей JWT-токенов.
- **Google OAuth 2.0**: авторизация через Google с перенаправлением на `GOOGLE_FINAL_REDIRECT_URI`.
- **SMS-подтверждение**: выдача одноразовых кодов через SMSC и подтверждение входа по коду.

## Технический стек
- Python 3.12, FastAPI, Uvicorn
- SQLAlchemy 2 (async) + Alembic, PostgreSQL (DEV/STAGE/PROD), SQLite (TEST)
- Pydantic Settings для конфигурации, python-jose и passlib для безопасности
- Gunicorn, SQLAdmin, aiofiles, httpx, Sentry SDK
- Управление зависимостями через `uv`

## Архитектура
- **Модульный монолит**: доменные области (пользователи, проекты, платежи и т.д.) инкапсулированы в отдельных пакетах под `app/v1`, каждый со своим `router`, `schemas`, `service` и `use_cases`.
- **Слоистая организация**: запросы проходят через слой API (FastAPI роутеры), бизнес-логику (use case/service) и слой доступа к данным (`dao`, `models`, `database`).
- **Версионирование API**: основная версия `v1`, при необходимости добавляются альтернативные префиксы (`/app/v2/auth`).
- **Инфраструктурные сервисы**: конфигурация через `settings.py`, единая точка подключения к БД (`app/v1/dao/database.py`), интеграции с платежами и S3 оформлены отдельными модулями.
- **Административный контур**: SQLAdmin использует те же ORM-модели, что и основной API, избегая дублирования логики.

## Требования
- Python 3.12+
- PostgreSQL 14+ для режимов DEV/STAGE/PROD
- Доступ к S3-совместимому хранилищу и учетные данные платежных провайдеров (для соответствующих функций)
- Установленный `uv` 0.4+

## Быстрый старт

### 1. Клонирование репозитория
```bash
git clone <repo-url>
cd sadaka_app
```

### 2. Установка зависимостей
**Установка зависимостей через uv:**
```bash
uv sync --frozen
```
> Убедитесь, что `uv` установлен глобально (инструкции доступны на странице проекта `astral-sh/uv`).

### 3. Создание `.env`
Создайте файл `.env` в корне проекта (если в команде есть готовый шаблон — воспользуйтесь им) и заполните значения переменных (см. раздел ниже).

## Переменные окружения
Все переменные читаются из файла `.env` в корне проекта.

### Основные
- `MODE` — режим работы (`DEV`, `STAGE`, `PROD`, `TEST`)
- `SECRET_KEY` — секрет для подписи JWT и админ-панели
- `ALGORITHM` — алгоритм шифрования JWT (например, `HS256`)

### Google OAuth
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_CALLBACK_URI`
- `GOOGLE_FINAL_REDIRECT_URI`

### Файловое хранилище (S3-совместимое)
- `S3_ACCESS_KEY`
- `S3_SECRET_KEY`
- `S3_BUCKET_NAME`
- `S3_ENDPOINT_URL`
- `S3_FILE_BASE_URL`

### Подключения к БД
- DEV: `POSTGRES_DEV_USER`, `POSTGRES_DEV_PASSWORD`, `POSTGRES_DEV_HOST`, `POSTGRES_DEV_DB_NAME`
- STAGE: `POSTGRES_STAGE_USER`, `POSTGRES_STAGE_PASSWORD`, `POSTGRES_STAGE_HOST`, `POSTGRES_STAGE_DB_NAME`
- TEST: `POSTGRES_TEST_USER`, `POSTGRES_TEST_PASSWORD`, `POSTGRES_TEST_HOST`, `POSTGRES_TEST_DB_NAME`

### Платежные провайдеры
- YooKassa: `YOOKASSA_TEST_SECRET_KEY`, `YOOKASSA_TEST_SHOP_ID`
- Т-Банк: `T_BANK_API_URL`, `T_BANK_WEBHOOK_URL`, `T_BANK_TERMINAL_KEY`, `T_BANK_PASSWORD`

### SMS
- `SMSC_LOGIN`
- `SMSC_PASSWORD`

## Локальный запуск
1. Установите `MODE=DEV` в `.env`.
2. Подготовьте базу данных (создайте БД в PostgreSQL и выдайте доступ пользователю).
3. Запустите миграции:
   ```bash
   uv run alembic upgrade head
   ```
4. Запустите приложение:
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
5. Полезные точки входа:
   - API документация Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`
   - Админ-панель SQLAdmin: `http://localhost:8000/admin`

## Миграции базы данных
- Создать новую миграцию:
  ```bash
  uv run alembic revision --autogenerate -m "Short description"
  ```
- Применить миграции:
  ```bash
  uv run alembic upgrade head
  ```
- Откатить на один шаг:
  ```bash
  uv run alembic downgrade -1
  ```
`alembic.ini` настроен на `script_location = app/migration`.

## Тестирование
- Установите dev-зависимости:
  ```bash
  uv sync --group dev
  ```
- Запустите тесты (переменная `MODE` автоматически переопределяется в `app/conftest.py`):
  ```bash
  uv run pytest
  ```
- Для проверки производительности:
  ```bash
  uv run pytest app/tests/performance
  ```

## Нагрузочное тестирование
Locust-сценарий расположен в `load_tests/locustfile.py`.
```bash
uv sync --group dev
uv run locust -f load_tests/locustfile.py
```
Полезные переменные окружения:
- `SADAKA_BASE_URL` — базовый URL API (по умолчанию `https://sadaka.pro`)
- `SADAKA_RATING_ENDPOINT` — путь рейтингового эндпоинта (`/app/v1/ratings/total_info`)
- `SADAKA_REFRESH_ENDPOINT` — эндпоинт обновления токена (`/app/v1/auth/refresh`)
- `SADAKA_PROJECT_STATUS` — фильтр проектов (`active`, `finished`, `all`)
- `SADAKA_PROJECTS_PAGE`, `SADAKA_PROJECTS_LIMIT` — параметры пагинации

Запуск в headless-режиме:
```bash
uv run locust -f load_tests/locustfile.py --headless -u 10 -r 2 --run-time 5m
```

## Подготовка к продакшену
- Сборка зависимостей: `uv sync --frozen --no-dev`
- Запуск приложения через Gunicorn:
  ```bash
  uv run gunicorn app.main:app \
    --workers 6 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
  ```
- Для фоновой работы можно использовать `systemd` или `supervisor`. Логи Gunicorn настраиваются ключами `--access-logfile` и `--error-logfile`.

## Структура проекта
```text
app/
├── main.py                 # Точка входа FastAPI
├── settings.py             # Конфигурация через Pydantic Settings
├── admin/                  # SQLAdmin-панель
├── v1/                     # Основной API (auth, users, projects, payments и др.)
├── tests/                  # Pytest-сценарии
├── migration/              # Alembic-скрипты
├── models/                 # ORM-модели
├── utils/                  # Утилиты и вспомогательные скрипты
└── static/                 # Статические файлы
load_tests/                 # Нагрузочные сценарии Locust
frontend/                   # Фронтенд-проект (если требуется)
data/                       # Локальные файлы БД (SQLite для тестов)
pyproject.toml              # Описание пакета и зависимостей
alembic.ini                 # Конфигурация Alembic
```

## Дополнительные инструменты
- Прогон линтеров: `uv run ruff check .` и `uv run black .`
- Предкоммит-хуки: `uv run pre-commit install` и `uv run pre-commit run --all-files`
- Скрипт `app/profiler.py` включает профилирование запросов и пула соединений

## Полезные советы
- Для локальной разработки используйте отдельный `.env` c `MODE=DEV`. Для тестов не меняйте `MODE` вручную — Pytest подставляет `TEST`.
- При обновлении зависимостей фиксируйте версии через `uv lock` и коммитьте `uv.lock`.
- Храните секреты (ключи платежей, S3 и т.д.) только в защищенных хранилищах, не коммитьте `.env`.
