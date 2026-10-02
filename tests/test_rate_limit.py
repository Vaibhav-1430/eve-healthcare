import pytest
from httpx import AsyncClient
from app.core.redis import get_redis_client


@pytest.mark.asyncio
async def test_rate_limiting_enforcement(client: AsyncClient):
    redis = get_redis_client()
    try:
        await redis.ping()
    except Exception:
        pytest.skip("Redis is not available in test environment")

    # Flush rate limiter keys in test db
    await redis.flushdb()

    # Rate limit on /auth/signup is configured to 10 per minute
    # Send 10 allowed requests (which may fail validation or signup, but pass rate limit)
    hit_429 = False
    for i in range(15):
        resp = await client.post(
            "/auth/login",
            json={"email": f"ratetest{i}@evehealthcare.com", "password": "WrongPassword123!"},
        )
        if resp.status_code == 429:
            hit_429 = True
            assert "Rate limit exceeded" in resp.json()["detail"]
            assert "Retry-After" in resp.headers
            break

    assert hit_429 is True
