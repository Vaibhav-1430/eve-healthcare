import math
import uuid
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.core.redis import delete_cache_pattern, get_cached_json, set_cached_json
from app.models.diagnostic_centre import DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest
from app.schemas.diagnostic import CentreCreateRequest, TestCreateRequest


async def create_centre(db: AsyncSession, payload: CentreCreateRequest) -> DiagnosticCentre:
    centre = DiagnosticCentre(
        name=payload.name.strip(),
        location=payload.location.strip(),
    )
    db.add(centre)
    await db.commit()
    await db.refresh(centre)

    # Invalidate centre cache
    await delete_cache_pattern("centres:list:*")

    logger.info(
        f"Diagnostic centre created: {centre.id}",
        extra={"extra_data": {"centre_id": str(centre.id), "name": centre.name}}
    )
    return centre


async def list_centres(db: AsyncSession, page: int, page_size: int) -> dict:
    cache_key = f"centres:list:{page}:{page_size}"
    cached = await get_cached_json(cache_key)
    if cached:
        return cached

    count_stmt = select(func.count()).select_from(DiagnosticCentre)
    total = (await db.execute(count_stmt)).scalar() or 0

    offset = (page - 1) * page_size
    stmt = (
        select(DiagnosticCentre)
        .order_by(DiagnosticCentre.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    centres = result.scalars().all()

    pages = math.ceil(total / page_size) if total > 0 else 0
    data = {
        "items": [
            {
                "id": str(c.id),
                "name": c.name,
                "location": c.location,
                "created_at": c.created_at.isoformat(),
            }
            for c in centres
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages,
    }

    await set_cached_json(cache_key, data, ttl=60)
    return data


async def get_centre_by_id(db: AsyncSession, centre_id: uuid.UUID) -> DiagnosticCentre:
    stmt = select(DiagnosticCentre).where(DiagnosticCentre.id == centre_id)
    centre = (await db.execute(stmt)).scalar_one_or_none()
    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnostic centre with ID {centre_id} not found",
        )
    return centre


async def create_test(db: AsyncSession, centre_id: uuid.UUID, payload: TestCreateRequest) -> DiagnosticTest:
    await get_centre_by_id(db, centre_id)

    test = DiagnosticTest(
        centre_id=centre_id,
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else None,
        price=payload.price,
    )
    db.add(test)
    await db.commit()
    await db.refresh(test)

    # Invalidate tests cache for this centre
    await delete_cache_pattern(f"tests:list:{centre_id}:*")

    logger.info(
        f"Diagnostic test created: {test.id}",
        extra={"extra_data": {"test_id": str(test.id), "centre_id": str(centre_id)}}
    )
    return test


async def list_tests_by_centre(db: AsyncSession, centre_id: uuid.UUID, page: int, page_size: int) -> dict:
    await get_centre_by_id(db, centre_id)

    cache_key = f"tests:list:{centre_id}:{page}:{page_size}"
    cached = await get_cached_json(cache_key)
    if cached:
        return cached

    count_stmt = (
        select(func.count())
        .select_from(DiagnosticTest)
        .where(DiagnosticTest.centre_id == centre_id)
    )
    total = (await db.execute(count_stmt)).scalar() or 0

    offset = (page - 1) * page_size
    stmt = (
        select(DiagnosticTest)
        .where(DiagnosticTest.centre_id == centre_id)
        .order_by(DiagnosticTest.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    tests = (await db.execute(stmt)).scalars().all()

    pages = math.ceil(total / page_size) if total > 0 else 0
    data = {
        "items": [
            {
                "id": str(t.id),
                "centre_id": str(t.centre_id),
                "name": t.name,
                "description": t.description,
                "price": str(t.price),
                "created_at": t.created_at.isoformat(),
            }
            for t in tests
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages,
    }

    await set_cached_json(cache_key, data, ttl=60)
    return data


async def get_test_by_id(db: AsyncSession, test_id: uuid.UUID) -> DiagnosticTest:
    stmt = select(DiagnosticTest).where(DiagnosticTest.id == test_id)
    test = (await db.execute(stmt)).scalar_one_or_none()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnostic test with ID {test_id} not found",
        )
    return test
