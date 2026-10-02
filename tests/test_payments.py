from datetime import datetime, timezone
import uuid
import pytest
from httpx import AsyncClient

from app.models.diagnostic_centre import DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest


@pytest.mark.asyncio
async def test_successful_simulated_payment(
    client: AsyncClient,
    auth_headers: dict,
    test_centre: DiagnosticCentre,
    test_diagnostic_test: DiagnosticTest,
):
    # 1. Create booking
    booking_resp = await client.post(
        "/bookings/",
        json={
            "diagnostic_centre_id": str(test_centre.id),
            "diagnostic_test_id": str(test_diagnostic_test.id),
            "appointment_datetime": datetime.now(timezone.utc).isoformat(),
        },
        headers=auth_headers,
    )
    booking_id = booking_resp.json()["id"]

    # 2. Simulate payment SUCCESS
    pay_resp = await client.post(
        "/payments/",
        json={"booking_id": booking_id, "simulated_status": "SUCCESS"},
        headers=auth_headers,
    )
    assert pay_resp.status_code == 201
    pay_data = pay_resp.json()
    assert pay_data["status"] == "SUCCESS"
    assert float(pay_data["amount"]) == float(test_diagnostic_test.price)
    assert "provider_reference" in pay_data

    # 3. Verify booking status changed to CONFIRMED
    updated_booking = await client.get(f"/bookings/{booking_id}", headers=auth_headers)
    assert updated_booking.json()["status"] == "CONFIRMED"


@pytest.mark.asyncio
async def test_failed_simulated_payment(
    client: AsyncClient,
    auth_headers: dict,
    test_centre: DiagnosticCentre,
    test_diagnostic_test: DiagnosticTest,
):
    booking_resp = await client.post(
        "/bookings/",
        json={
            "diagnostic_centre_id": str(test_centre.id),
            "diagnostic_test_id": str(test_diagnostic_test.id),
            "appointment_datetime": datetime.now(timezone.utc).isoformat(),
        },
        headers=auth_headers,
    )
    booking_id = booking_resp.json()["id"]

    # Simulate payment FAILED
    pay_resp = await client.post(
        "/payments/",
        json={"booking_id": booking_id, "simulated_status": "FAILED"},
        headers=auth_headers,
    )
    assert pay_resp.status_code == 201
    assert pay_resp.json()["status"] == "FAILED"

    # Verify booking status changed to FAILED
    updated_booking = await client.get(f"/bookings/{booking_id}", headers=auth_headers)
    assert updated_booking.json()["status"] == "FAILED"


@pytest.mark.asyncio
async def test_duplicate_payment_fails(
    client: AsyncClient,
    auth_headers: dict,
    test_centre: DiagnosticCentre,
    test_diagnostic_test: DiagnosticTest,
):
    booking_resp = await client.post(
        "/bookings/",
        json={
            "diagnostic_centre_id": str(test_centre.id),
            "diagnostic_test_id": str(test_diagnostic_test.id),
            "appointment_datetime": datetime.now(timezone.utc).isoformat(),
        },
        headers=auth_headers,
    )
    booking_id = booking_resp.json()["id"]

    # First payment succeeds
    await client.post(
        "/payments/",
        json={"booking_id": booking_id, "simulated_status": "SUCCESS"},
        headers=auth_headers,
    )

    # Second payment must be rejected
    second_pay = await client.post(
        "/payments/",
        json={"booking_id": booking_id, "simulated_status": "SUCCESS"},
        headers=auth_headers,
    )
    assert second_pay.status_code == 400
    assert "Payment cannot be processed" in second_pay.json()["detail"]


@pytest.mark.asyncio
async def test_payment_for_non_existent_booking(client: AsyncClient, auth_headers: dict):
    fake_booking_id = str(uuid.uuid4())
    response = await client.post(
        "/payments/",
        json={"booking_id": fake_booking_id, "simulated_status": "SUCCESS"},
        headers=auth_headers,
    )
    assert response.status_code == 404
