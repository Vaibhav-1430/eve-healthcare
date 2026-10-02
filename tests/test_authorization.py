from datetime import datetime, timezone
import pytest
from httpx import AsyncClient

from app.models.diagnostic_centre import DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest


@pytest.mark.asyncio
async def test_user_cannot_access_another_users_booking(
    client: AsyncClient,
    auth_headers: dict,
    second_auth_headers: dict,
    test_centre: DiagnosticCentre,
    test_diagnostic_test: DiagnosticTest,
):
    # User A creates a booking
    create_resp = await client.post(
        "/bookings/",
        json={
            "diagnostic_centre_id": str(test_centre.id),
            "diagnostic_test_id": str(test_diagnostic_test.id),
            "appointment_datetime": datetime.now(timezone.utc).isoformat(),
        },
        headers=auth_headers,
    )
    user_a_booking_id = create_resp.json()["id"]

    # User B attempts to access User A's booking
    resp = await client.get(f"/bookings/{user_a_booking_id}", headers=second_auth_headers)
    assert resp.status_code == 403
    assert "do not have permission" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_user_cannot_cancel_another_users_booking(
    client: AsyncClient,
    auth_headers: dict,
    second_auth_headers: dict,
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
    user_a_booking_id = create_resp.json()["id"]

    # User B attempts to cancel User A's booking
    cancel_resp = await client.post(
        f"/bookings/{user_a_booking_id}/cancel",
        headers=second_auth_headers,
    )
    assert cancel_resp.status_code == 403
    assert "do not have permission" in cancel_resp.json()["detail"]


@pytest.mark.asyncio
async def test_user_cannot_pay_for_another_users_booking(
    client: AsyncClient,
    auth_headers: dict,
    second_auth_headers: dict,
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
    user_a_booking_id = create_resp.json()["id"]

    # User B attempts to trigger payment for User A's booking
    pay_resp = await client.post(
        "/payments/",
        json={"booking_id": user_a_booking_id, "simulated_status": "SUCCESS"},
        headers=second_auth_headers,
    )
    assert pay_resp.status_code == 403
    assert "do not have permission" in pay_resp.json()["detail"]


@pytest.mark.asyncio
async def test_user_booking_list_isolation(
    client: AsyncClient,
    auth_headers: dict,
    second_auth_headers: dict,
    test_centre: DiagnosticCentre,
    test_diagnostic_test: DiagnosticTest,
):
    # User A creates a booking
    await client.post(
        "/bookings/",
        json={
            "diagnostic_centre_id": str(test_centre.id),
            "diagnostic_test_id": str(test_diagnostic_test.id),
            "appointment_datetime": datetime.now(timezone.utc).isoformat(),
        },
        headers=auth_headers,
    )

    # User B's list should be empty
    user_b_list = await client.get("/bookings/", headers=second_auth_headers)
    assert user_b_list.status_code == 200
    assert user_b_list.json()["total"] == 0
    assert len(user_b_list.json()["items"]) == 0
