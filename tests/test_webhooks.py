import asyncio
from datetime import datetime, timezone
import uuid
import pytest
from httpx import AsyncClient

from app.models.diagnostic_centre import DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest


async def _create_test_payment_fixture(
    client: AsyncClient,
    auth_headers: dict,
    test_centre: DiagnosticCentre,
    test_diagnostic_test: DiagnosticTest,
) -> tuple[str, str]:
    # Creates a booking and an initial payment record in PENDING status
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

    # Trigger initial simulated payment in PENDING status
    pay_resp = await client.post(
        "/payments/",
        json={"booking_id": booking_id, "simulated_status": "PENDING"},
        headers=auth_headers,
    )
    provider_ref = pay_resp.json()["provider_reference"]
    return booking_id, provider_ref


@pytest.mark.asyncio
async def test_webhook_successful_processing(
    client: AsyncClient,
    auth_headers: dict,
    test_centre: DiagnosticCentre,
    test_diagnostic_test: DiagnosticTest,
):
    booking_id, provider_ref = await _create_test_payment_fixture(
        client, auth_headers, test_centre, test_diagnostic_test
    )

    event_id = f"evt_{uuid.uuid4().hex}"
    webhook_payload = {
        "event_id": event_id,
        "payment_reference": provider_ref,
        "status": "SUCCESS",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    response = await client.post("/payments/webhook/", json=webhook_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "processed"
    assert response.json()["event_id"] == event_id

    # Verify booking status transitioned
    booking_check = await client.get(f"/bookings/{booking_id}", headers=auth_headers)
    assert booking_check.json()["status"] == "CONFIRMED"


@pytest.mark.asyncio
async def test_webhook_idempotency_duplicate_events(
    client: AsyncClient,
    auth_headers: dict,
    test_centre: DiagnosticCentre,
    test_diagnostic_test: DiagnosticTest,
):
    booking_id, provider_ref = await _create_test_payment_fixture(
        client, auth_headers, test_centre, test_diagnostic_test
    )

    event_id = f"evt_idempotent_{uuid.uuid4().hex}"
    webhook_payload = {
        "event_id": event_id,
        "payment_reference": provider_ref,
        "status": "SUCCESS",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # First delivery
    resp1 = await client.post("/payments/webhook/", json=webhook_payload)
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "processed"

    # Second delivery with identical event_id
    resp2 = await client.post("/payments/webhook/", json=webhook_payload)
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "already_processed"
    assert "already been processed" in resp2.json()["message"]

    # Multiple deliveries (e.g. 5 repeated webhook retries)
    for _ in range(5):
        retry_resp = await client.post("/payments/webhook/", json=webhook_payload)
        assert retry_resp.status_code == 200
        assert retry_resp.json()["status"] == "already_processed"

    # Ensure booking remained CONFIRMED and was not corrupted
    booking_check = await client.get(f"/bookings/{booking_id}", headers=auth_headers)
    assert booking_check.json()["status"] == "CONFIRMED"


@pytest.mark.asyncio
async def test_webhook_unknown_payment_reference(client: AsyncClient):
    webhook_payload = {
        "event_id": f"evt_unknown_{uuid.uuid4().hex}",
        "payment_reference": "pay_nonexistent_ref_123",
        "status": "SUCCESS",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    response = await client.post("/payments/webhook/", json=webhook_payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_concurrent_duplicate_webhooks(
    client: AsyncClient,
    auth_headers: dict,
    test_centre: DiagnosticCentre,
    test_diagnostic_test: DiagnosticTest,
):
    booking_id, provider_ref = await _create_test_payment_fixture(
        client, auth_headers, test_centre, test_diagnostic_test
    )

    event_id = f"evt_concurrent_{uuid.uuid4().hex}"
    webhook_payload = {
        "event_id": event_id,
        "payment_reference": provider_ref,
        "status": "SUCCESS",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Send 4 concurrent requests with the exact same event_id
    tasks = [
        client.post("/payments/webhook/", json=webhook_payload)
        for _ in range(4)
    ]
    responses = await asyncio.gather(*tasks)

    # All should return 200 OK (one will be 'processed', others 'already_processed')
    statuses = [r.status_code for r in responses]
    assert all(code == 200 for code in statuses)

    outcomes = [r.json()["status"] for r in responses]
    assert "processed" in outcomes or "already_processed" in outcomes
