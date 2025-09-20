import time

from loguru import logger
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.middleware.base import BaseHTTPMiddleware


# -------------------------
# 1. Middleware для FastAPI
# -------------------------
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        logger.info(f"⏱ {request.method} {request.url.path} took {elapsed:.3f}s")
        return response


# -------------------------
# 2. Логирование SQL
# -------------------------
def setup_sql_logging(engine: AsyncEngine):
    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault("query_start_time", []).append(time.perf_counter())

    @event.listens_for(engine.sync_engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.perf_counter() - conn.info["query_start_time"].pop(-1)
        short_sql = statement.strip().splitlines()[0]
        logger.info(f"📄 SQL {total:.3f}s: {short_sql}...")


# -------------------------
# 3. Логирование пула
# -------------------------
def setup_pool_logging(engine: AsyncEngine):
    @event.listens_for(engine.sync_engine, "checkout")
    def checkout(dbapi_connection, connection_record, connection_proxy):
        connection_record.info["checkout_start"] = time.perf_counter()

    @event.listens_for(engine.sync_engine, "checkin")
    def checkin(dbapi_connection, connection_record):
        start = connection_record.info.pop("checkout_start", None)
        if start is not None:
            elapsed = time.perf_counter() - start
            logger.info(f"🔌 Connection from pool held for {elapsed:.3f}s")
