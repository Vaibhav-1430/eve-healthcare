import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.booking import Booking, BookingStatus, can_transition_booking
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentSimulateRequest


async def simulate_payment(
    db: AsyncSession,
    user_id: uuid.UUID,
    payload: PaymentSimulateRequest,
) -> Payment:
    # Lock the booking row for update to prevent concurrent duplicate payments
    stmt = (
        select(Booking)
        .where(Booking.id == payload.booking_id)
        .with_for_update()
    )
    booking = (await db.execute(stmt)).scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {payload.booking_id} not found",
        )

    if booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to pay for this booking",
        )

    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment cannot be processed. Booking status is '{booking.status}'.",
        )

    pay_stmt = (
        select(Payment)
        .where(Payment.booking_id == booking.id)
        .with_for_update()
    )
    existing_payment = (await db.execute(pay_stmt)).scalar_one_or_none()
    if existing_payment and existing_payment.status == PaymentStatus.SUCCESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A successful payment has already been recorded for this booking",
        )

    if payload.simulated_status == PaymentStatus.SUCCESS:
        target_booking_status = BookingStatus.CONFIRMED
    elif payload.simulated_status == PaymentStatus.FAILED:
        target_booking_status = BookingStatus.FAILED
    else:
        target_booking_status = BookingStatus.PENDING

    if target_booking_status != booking.status and not can_transition_booking(booking.status, target_booking_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Illegal state transition from {booking.status} to {target_booking_status}",
        )

    # Generate unique payment reference
    provider_ref = f"pay_sim_{uuid.uuid4().hex[:16]}"

    if existing_payment:
        # Update existing failed/pending payment
        existing_payment.status = payload.simulated_status
        existing_payment.provider_reference = provider_ref
        payment = existing_payment
    else:
        # Create payment record - amount is strictly derived from the booking snapshot
        payment = Payment(
            booking_id=booking.id,
            amount=booking.amount,
            status=payload.simulated_status,
            provider_reference=provider_ref,
        )
        db.add(payment)

    booking.status = target_booking_status

    await db.commit()
    await db.refresh(payment)

    logger.info(
        f"Simulated payment processed: {payment.id}",
        extra={
            "extra_data": {
                "payment_id": str(payment.id),
                "booking_id": str(booking.id),
                "amount": str(payment.amount),
                "status": payment.status,
                "provider_ref": payment.provider_reference,
            }
        }
    )
    return payment
