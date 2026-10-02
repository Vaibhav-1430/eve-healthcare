import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.pagination import PaginationParams, get_pagination
from app.schemas.common import PaginatedResponse
from app.schemas.diagnostic import (
    CentreCreateRequest,
    CentreResponse,
    TestCreateRequest,
    TestResponse,
)
from app.services.centre_service import (
    create_centre,
    create_test,
    get_centre_by_id,
    get_test_by_id,
    list_centres,
    list_tests_by_centre,
)

router = APIRouter(tags=["Diagnostic Centres & Tests"])


@router.post(
    "/centres/",
    response_model=CentreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new diagnostic centre",
)
async def create_new_centre(
    payload: CentreCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    centre = await create_centre(db, payload)
    return CentreResponse.model_validate(centre)


@router.get(
    "/centres/",
    response_model=PaginatedResponse[CentreResponse],
    status_code=status.HTTP_200_OK,
    summary="List diagnostic centres with pagination",
)
async def get_centres(
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
):
    return await list_centres(db, pagination.page, pagination.page_size)


@router.get(
    "/centres/{centre_id}",
    response_model=CentreResponse,
    status_code=status.HTTP_200_OK,
    summary="Get details of a diagnostic centre by ID",
)
async def get_centre(
    centre_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    centre = await get_centre_by_id(db, centre_id)
    return CentreResponse.model_validate(centre)


@router.post(
    "/centres/{centre_id}/tests",
    response_model=TestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a diagnostic test to a centre",
)
async def add_test_to_centre(
    centre_id: uuid.UUID,
    payload: TestCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    test = await create_test(db, centre_id, payload)
    return TestResponse.model_validate(test)


@router.get(
    "/centres/{centre_id}/tests",
    response_model=PaginatedResponse[TestResponse],
    status_code=status.HTTP_200_OK,
    summary="List tests offered by a diagnostic centre with pagination",
)
async def get_tests_for_centre(
    centre_id: uuid.UUID,
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
):
    return await list_tests_by_centre(db, centre_id, pagination.page, pagination.page_size)


@router.get(
    "/tests/{test_id}",
    response_model=TestResponse,
    status_code=status.HTTP_200_OK,
    summary="Get details of a diagnostic test by ID",
)
async def get_test(
    test_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    test = await get_test_by_id(db, test_id)
    return TestResponse.model_validate(test)
