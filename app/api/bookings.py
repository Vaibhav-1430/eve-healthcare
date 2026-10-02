import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.pagination import PaginationParams, get_pagination
from app.models.user import User
from app.schemas.booking import BookingCreateRequest, BookingResponse
from app.schemas.common import PaginatedResponse
from app.services.booking_service import (
    cancel_booking,
    create_booking,
    get_booking_by_id,
    list_user_bookings,
)

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new diagnostic test booking",
)
async def create_new_booking(
    payload: BookingCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_booking(db, current_user.id, payload)


@router.get(
    "/",
    response_model=PaginatedResponse[BookingResponse],
    status_code=status.HTTP_200_OK,
    summary="List bookings belonging to the authenticated user",
)
async def get_user_bookings(
    pagination: PaginationParams = Depends(get_pagination),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_user_bookings(db, current_user.id, pagination.page, pagination.page_size)


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get details of a specific booking",
)
async def get_booking(
    booking_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_booking_by_id(db, booking_id, current_user.id)


@router.post(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel a pending booking",
)
async def cancel_user_booking(
    booking_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await cancel_booking(db, booking_id, current_user.id)
