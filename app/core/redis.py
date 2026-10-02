import json
from typing import Any
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger

redis_client: aioredis.Redis | None = None


def get_redis_client() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2.0,
        )
    return redis_client


async def close_redis_client():
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None


async def get_cached_json(key: str) -> Any | None:
    try:
        client = get_redis_client()
        val = await client.get(key)
        return json.loads(val) if val else None
    except Exception as e:
        logger.warning(f"Redis get cache failed: {e}")
        return None


async def set_cached_json(key: str, value: Any, ttl: int = settings.CACHE_TTL_SECONDS):
    try:
        client = get_redis_client()
        await client.set(key, json.dumps(value), ex=ttl)
    except Exception as e:
        logger.warning(f"Redis set cache failed: {e}")


async def delete_cache_pattern(pattern: str):
    try:
        client = get_redis_client()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
    except Exception as e:
        logger.warning(f"Redis delete cache pattern failed: {e}")
