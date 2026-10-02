from datetime import datetime, timezone
import uuid
import pytest
from httpx import AsyncClient

from app.models.diagnostic_centre import DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest
from app.models.user import User


@pytest.mark.asyncio
async def test_create_booking_success(
    client: AsyncClient,
    auth_headers: dict,
    test_centre: DiagnosticCentre,
    test_diagnostic_test: DiagnosticTest,
):
    payload = {
        "diagnostic_centre_id": str(test_centre.id),
        "diagnostic_test_id": str(test_diagnostic_test.id),
        "appointment_datetime": datetime.now(timezone.utc).isoformat(),
    }
    response = await client.post("/bookings/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "PENDING"
    # Booking amount must be copied directly from the test's price in the database
    assert float(data["amount"]) == float(test_diagnostic_test.price)
    assert data["diagnostic_centre_id"] == str(test_centre.id)
    assert data["diagnostic_test_id"] == str(test_diagnostic_test.id)


@pytest.mark.asyncio
async def test_create_booking_invalid_centre(
    client: AsyncClient,
    auth_headers: dict,
    test_diagnostic_test: DiagnosticTest,
):
    fake_centre_id = str(uuid.uuid4())
    payload = {
        "diagnostic_centre_id": fake_centre_id,
        "diagnostic_test_id": str(test_diagnostic_test.id),
        "appointment_datetime": datetime.now(timezone.utc).isoformat(),
    }
    response = await client.post("/bookings/", json=payload, headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_booking_invalid_test(
    client: AsyncClient,
    auth_headers: dict,
    test_centre: DiagnosticCentre,
):
    fake_test_id = str(uuid.uuid4())
    payload = {
        "diagnostic_centre_id": str(test_centre.id),
        "diagnostic_test_id": fake_test_id,
        "appointment_datetime": datetime.now(timezone.utc).isoformat(),
    }
    response = await client.post("/bookings/", json=payload, headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_booking_test_belongs_to_different_centre(
    client: AsyncClient,
    auth_headers: dict,
    test_diagnostic_test: DiagnosticTest,
):
    # Create another centre
    other_centre_resp = await client.post(
        "/centres/",
        json={"name": "Different Diagnostic Hub", "location": "Whitefield"},
    )
    other_centre_id = other_centre_resp.json()["id"]

    # Try to book test_diagnostic_test (belongs to test_centre) with other_centre_id
    payload = {
        "diagnostic_centre_id": other_centre_id,
        "diagnostic_test_id": str(test_diagnostic_test.id),
        "appointment_datetime": datetime.now(timezone.utc).isoformat(),
    }
    response = await client.post("/bookings/", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "does not belong" in response.json()["detail"]


@pytest.mark.asyncio
async def test_cancel_booking_success(
    client: AsyncClient,
    auth_headers: dict,
    test_centre: DiagnosticCentre,
    test_diagnostic_test: DiagnosticTest,
):
    # Create booking
    create_resp = await client.post(
        "/bookings/",
        json={
            "diagnostic_centre_id": str(test_centre.id),
            "diagnostic_test_id": str(test_diagnostic_test.id),
            "appointment_datetime": datetime.now(timezone.utc).isoformat(),
        },
        headers=auth_headers,
    )
    booking_id = create_resp.json()["id"]

    # Cancel booking
    cancel_resp = await client.post(f"/bookings/{booking_id}/cancel", headers=auth_headers)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_cancel_already_cancelled_booking_fails(
    client: AsyncClient,
    auth_headers: dict,
    test_centre: DiagnosticCentre,
    test_diagnostic_test: DiagnosticTest,
):
    create_resp = await client.post(
        "/bookings/",
        json={
            "diagnostic_centre_id": str(test_centre.id),
            "diagnostic_test_id": str(test_diagnostic_test.id),
            "appointment_datetime": datetime.now(timezone.utc).isoformat(),
        },
        headers=auth_headers,
    )
    booking_id = create_resp.json()["id"]

    # First cancel succeeds
    await client.post(f"/bookings/{booking_id}/cancel", headers=auth_headers)

    # Second cancel must fail with 400 (invalid state transition)
    second_cancel = await client.post(f"/bookings/{booking_id}/cancel", headers=auth_headers)
    assert second_cancel.status_code == 400
    assert "Cannot cancel booking in status" in second_cancel.json()["detail"]


@pytest.mark.asyncio
async def test_list_bookings_pagination(
    client: AsyncClient,
    auth_headers: dict,
    test_centre: DiagnosticCentre,
    test_diagnostic_test: DiagnosticTest,
):
    for _ in range(3):
        await client.post(
            "/bookings/",
            json={
                "diagnostic_centre_id": str(test_centre.id),
                "diagnostic_test_id": str(test_diagnostic_test.id),
                "appointment_datetime": datetime.now(timezone.utc).isoformat(),
            },
            headers=auth_headers,
        )

    response = await client.get("/bookings/?page=1&page_size=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 3
    assert data["pages"] == 2
