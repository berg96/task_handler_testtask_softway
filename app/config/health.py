import asyncio

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config.settings import settings


async def check_redis():
    client = await Redis.from_url(settings.REDIS_URL)
    try:
        await client.ping()
        return True
    except Exception:
        return False


async def check_db():
    engine = create_async_engine(settings.get_db_url())
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
    finally:
        await engine.dispose()


async def run_health_check():
    results = await asyncio.gather(check_redis(), check_db())
    if not all(results):
        return False
    return True
