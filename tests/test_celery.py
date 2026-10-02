from decimal import Decimal
import uuid
import pytest
from app.models.booking import Booking, BookingStatus
from app.models.diagnostic_centre import DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.tasks.payment_tasks import send_payment_receipt_async
from app.tasks.webhook_tasks import process_webhook_async
from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
async def test_send_payment_receipt_task():
    result = send_payment_receipt_async(
        payment_id=str(uuid.uuid4()),
        booking_id=str(uuid.uuid4()),
        amount="499.00",
        recipient_email="patient@example.com",
    )
    assert result is True


@pytest.mark.asyncio
async def test_process_webhook_async_task(
    test_user: User,
    test_centre: DiagnosticCentre,
    test_diagnostic_test: DiagnosticTest,
):
    async with TestingSessionLocal() as session:
        booking = Booking(
            user_id=test_user.id,
            diagnostic_centre_id=test_centre.id,
            diagnostic_test_id=test_diagnostic_test.id,
            appointment_datetime=test_centre.created_at,
            amount=Decimal("499.00"),
            status=BookingStatus.PENDING,
        )
        session.add(booking)
        await session.commit()
        await session.refresh(booking)

        provider_ref = f"pay_async_{uuid.uuid4().hex[:12]}"
        payment = Payment(
            booking_id=booking.id,
            amount=Decimal("499.00"),
            status=PaymentStatus.PENDING,
            provider_reference=provider_ref,
        )
        session.add(payment)
        await session.commit()

    event_id = f"evt_async_{uuid.uuid4().hex}"
    payload = {
        "event_id": event_id,
        "payment_reference": provider_ref,
        "status": "SUCCESS",
    }

    # Execute task with test session factory
    result = process_webhook_async(payload, session_factory=TestingSessionLocal)
    assert result["status"] == "processed"
