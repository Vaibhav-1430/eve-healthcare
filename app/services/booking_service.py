import math
import uuid
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.booking import Booking, BookingStatus, can_transition_booking
from app.models.diagnostic_centre import DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest
from app.schemas.booking import BookingCreateRequest


async def create_booking(db: AsyncSession, user_id: uuid.UUID, payload: BookingCreateRequest) -> Booking:
    centre_stmt = select(DiagnosticCentre).where(DiagnosticCentre.id == payload.diagnostic_centre_id)
    centre = (await db.execute(centre_stmt)).scalar_one_or_none()
    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnostic centre {payload.diagnostic_centre_id} not found",
        )

    test_stmt = select(DiagnosticTest).where(DiagnosticTest.id == payload.diagnostic_test_id)
    test = (await db.execute(test_stmt)).scalar_one_or_none()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnostic test {payload.diagnostic_test_id} not found",
        )

    if test.centre_id != payload.diagnostic_centre_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The specified test does not belong to the selected diagnostic centre",
        )

    # Snapshot price at booking creation time
    booking = Booking(
        user_id=user_id,
        diagnostic_centre_id=payload.diagnostic_centre_id,
        diagnostic_test_id=payload.diagnostic_test_id,
        appointment_datetime=payload.appointment_datetime,
        amount=test.price,
        status=BookingStatus.PENDING,
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)

    logger.info(
        f"Booking created: {booking.id}",
        extra={
            "extra_data": {
                "booking_id": str(booking.id),
                "user_id": str(user_id),
                "amount": str(booking.amount),
                "status": booking.status,
            }
        }
    )
    return booking


async def list_user_bookings(db: AsyncSession, user_id: uuid.UUID, page: int, page_size: int) -> dict:
    count_stmt = (
        select(func.count())
        .select_from(Booking)
        .where(Booking.user_id == user_id)
    )
    total = (await db.execute(count_stmt)).scalar() or 0

    offset = (page - 1) * page_size
    stmt = (
        select(Booking)
        .where(Booking.user_id == user_id)
        .order_by(Booking.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    bookings = (await db.execute(stmt)).scalars().all()

    pages = math.ceil(total / page_size) if total > 0 else 0
    return {
        "items": bookings,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages,
    }


async def get_booking_by_id(db: AsyncSession, booking_id: uuid.UUID, user_id: uuid.UUID) -> Booking:
    stmt = select(Booking).where(Booking.id == booking_id)
    booking = (await db.execute(stmt)).scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found",
        )

    if booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this booking",
        )

    return booking


async def cancel_booking(db: AsyncSession, booking_id: uuid.UUID, user_id: uuid.UUID) -> Booking:
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .with_for_update()
    )
    booking = (await db.execute(stmt)).scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found",
        )

    if booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to cancel this booking",
        )

    if not can_transition_booking(booking.status, BookingStatus.CANCELLED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel booking in status '{booking.status}'. Only PENDING bookings can be cancelled.",
        )

    booking.status = BookingStatus.CANCELLED
    await db.commit()
    await db.refresh(booking)

    logger.info(
        f"Booking cancelled: {booking.id}",
        extra={"extra_data": {"booking_id": str(booking.id), "user_id": str(user_id)}}
    )
    return booking
