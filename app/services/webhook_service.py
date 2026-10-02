from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.booking import Booking, BookingStatus, can_transition_booking
from app.models.payment import Payment, PaymentStatus
from app.models.webhook_event import WebhookEvent, WebhookStatus
from app.schemas.webhook import PaymentWebhookRequest


async def process_payment_webhook(
    db: AsyncSession,
    payload: PaymentWebhookRequest,
) -> tuple[str, str]:
    event_stmt = (
        select(WebhookEvent)
        .where(WebhookEvent.event_id == payload.event_id)
        .with_for_update()
    )
    existing_event = (await db.execute(event_stmt)).scalar_one_or_none()

    if existing_event and existing_event.status == WebhookStatus.PROCESSED:
        logger.info(
            f"Duplicate webhook received for event_id: {payload.event_id}",
            extra={"extra_data": {"event_id": payload.event_id, "action": "idempotent_skip"}}
        )
        return "already_processed", f"Event '{payload.event_id}' has already been processed."

    event = existing_event
    if not event:
        # Atomic registration: savepoint prevents aborting transaction on race condition unique violation
        try:
            async with db.begin_nested():
                event = WebhookEvent(
                    event_id=payload.event_id,
                    payment_reference=payload.payment_reference,
                    status=WebhookStatus.RECEIVED,
                    payload=payload.model_dump(mode="json"),
                )
                db.add(event)
                await db.flush()
        except IntegrityError:
            existing_again = (await db.execute(event_stmt)).scalar_one_or_none()
            if existing_again and existing_again.status == WebhookStatus.PROCESSED:
                return "already_processed", f"Event '{payload.event_id}' was processed concurrently."
            event = existing_again

    pay_stmt = (
        select(Payment)
        .where(Payment.provider_reference == payload.payment_reference)
        .with_for_update()
    )
    payment = (await db.execute(pay_stmt)).scalar_one_or_none()

    if not payment:
        if event:
            event.status = WebhookStatus.FAILED
            await db.commit()
        logger.warning(f"Webhook payment reference not found: {payload.payment_reference}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with reference '{payload.payment_reference}' not found",
        )

    booking_stmt = (
        select(Booking)
        .where(Booking.id == payment.booking_id)
        .with_for_update()
    )
    booking = (await db.execute(booking_stmt)).scalar_one_or_none()

    if not booking:
        if event:
            event.status = WebhookStatus.FAILED
            await db.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking for payment '{payload.payment_reference}' not found",
        )

    if payload.status == PaymentStatus.SUCCESS:
        target_payment_status = PaymentStatus.SUCCESS
        target_booking_status = BookingStatus.CONFIRMED
    else:
        target_payment_status = PaymentStatus.FAILED
        target_booking_status = BookingStatus.FAILED

    if payment.status == target_payment_status and booking.status == target_booking_status:
        if event:
            event.status = WebhookStatus.PROCESSED
            event.processed_at = datetime.now(timezone.utc)
        await db.commit()
        return "already_processed", f"Payment and booking are already in {payload.status} state."

    if not can_transition_booking(booking.status, target_booking_status):
        # Booking in terminal state: update payment without corrupting booking state
        payment.status = target_payment_status
        if event:
            event.status = WebhookStatus.PROCESSED
            event.processed_at = datetime.now(timezone.utc)
        await db.commit()
        return "processed_with_terminal_state", f"Booking is in terminal state '{booking.status}'."

    payment.status = target_payment_status
    booking.status = target_booking_status
    if event:
        event.status = WebhookStatus.PROCESSED
        event.processed_at = datetime.now(timezone.utc)

    await db.commit()

    logger.info(
        f"Webhook event {payload.event_id} processed: booking {booking.id} -> {booking.status}",
        extra={
            "extra_data": {
                "event_id": payload.event_id,
                "payment_ref": payload.payment_reference,
                "booking_id": str(booking.id),
                "status": booking.status,
            }
        }
    )
    return "processed", f"Webhook processed successfully for event '{payload.event_id}'."
