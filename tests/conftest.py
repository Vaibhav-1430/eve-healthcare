from decimal import Decimal
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import get_redis_client
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.diagnostic_centre import DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest
from app.models.user import User

test_engine = create_async_engine(
    settings.TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    # Clean tables before each test run to ensure strict isolation
    async with TestingSessionLocal() as session:
        await session.execute(
            text(
                "TRUNCATE TABLE webhook_events, payments, bookings, diagnostic_tests, diagnostic_centres, users CASCADE;"
            )
        )
        await session.commit()

    # Clean redis state between tests if redis is running
    try:
        redis = get_redis_client()
        await redis.flushdb()
    except Exception:
        pass

    yield


@pytest_asyncio.fixture
async def client():
    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user():
    async with TestingSessionLocal() as session:
        user = User(
            email="testuser@example.com",
            hashed_password=hash_password("Password123!"),
            full_name="Test User",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
def auth_headers(test_user: User):
    token = create_access_token(data={"sub": str(test_user.id), "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def second_user():
    async with TestingSessionLocal() as session:
        user = User(
            email="seconduser@example.com",
            hashed_password=hash_password("Password123!"),
            full_name="Second User",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
def second_auth_headers(second_user: User):
    token = create_access_token(data={"sub": str(second_user.id), "email": second_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_centre():
    async with TestingSessionLocal() as session:
        centre = DiagnosticCentre(
            name="Apollo Diagnostics",
            location="Indiranagar, Bengaluru",
        )
        session.add(centre)
        await session.commit()
        await session.refresh(centre)
        return centre


@pytest_asyncio.fixture
async def test_diagnostic_test(test_centre: DiagnosticCentre):
    async with TestingSessionLocal() as session:
        d_test = DiagnosticTest(
            centre_id=test_centre.id,
            name="Complete Blood Count (CBC)",
            description="Measures overall health and detects wide range of disorders",
            price=Decimal("499.00"),
        )
        session.add(d_test)
        await session.commit()
        await session.refresh(d_test)
        return d_test
