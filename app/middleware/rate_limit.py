import time
from fastapi import HTTPException, Request, status
from app.core.config import settings
from app.core.logging import logger
from app.core.redis import get_redis_client


class RateLimiter:
    def __init__(self, requests_per_minute: int | None = None, key_prefix: str = "rl"):
        self.requests_per_minute = requests_per_minute
        self.key_prefix = key_prefix

    async def __call__(self, request: Request):
        limit = self.requests_per_minute or settings.RATE_LIMIT_PER_MINUTE
        if limit <= 0:
            return

        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        current_minute = int(time.time() // 60)
        cache_key = f"{self.key_prefix}:{path}:{client_ip}:{current_minute}"

        try:
            redis = get_redis_client()
            # Increment request counter and set 60s TTL on first request
            count = await redis.incr(cache_key)
            if count == 1:
                await redis.expire(cache_key, 60)

            if count > limit:
                logger.warning(
                    f"Rate limit exceeded for IP {client_ip} on path {path}",
                    extra={"extra_data": {"client_ip": client_ip, "path": path, "count": count, "limit": limit}}
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Allowed: {limit} requests per minute.",
                    headers={"Retry-After": "60"},
                )
        except HTTPException:
            raise
        except Exception as e:
            # If Redis connection fails, fail open so business requests are not blocked
            logger.warning(f"Rate limiting skipped due to Redis error: {e}")
