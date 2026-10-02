import sys
from datetime import datetime, timezone
import uuid
import httpx

BASE_URL = "http://127.0.0.1:8000"

def log_step(step_num: int, title: str):
    print(f"\n[STEP {step_num}] {title}")

def main():
    import redis
    try:
        r = redis.from_url("redis://127.0.0.1:6379/0")
        rl_keys = r.keys("rl:*")
        if rl_keys:
            r.delete(*rl_keys)
    except Exception:
        pass

    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    # Health check
    health_resp = client.get("/health")
    assert health_resp.status_code == 200, f"Health check failed: {health_resp.text}"
    print(f"Health check OK: {health_resp.json()}")

    # 1. Signup User A
    log_step(1, "Signup User A")
    email_a = f"alice_{uuid.uuid4().hex[:6]}@example.com"
    signup_resp = client.post("/auth/signup", json={
        "email": email_a,
        "password": "Password123!",
        "full_name": "Alice Smith"
    })
    assert signup_resp.status_code == 201, f"Signup failed: {signup_resp.text}"
    user_a = signup_resp.json()
    assert "password" not in user_a and "hashed_password" not in user_a
    print(f"User A created: {user_a['id']} ({user_a['email']})")

    # 2. Login User A
    log_step(2, "Login User A")
    login_resp = client.post("/auth/login", json={
        "email": email_a,
        "password": "Password123!"
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"

    # 3. Get JWT
    log_step(3, "Get JWT Token")
    token_a = login_resp.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print("JWT Token acquired successfully.")

    # Signup & Login User B (for authorization / IDOR tests)
    email_b = f"bob_{uuid.uuid4().hex[:6]}@example.com"
    client.post("/auth/signup", json={
        "email": email_b,
        "password": "Password123!",
        "full_name": "Bob Jones"
    })
    login_b = client.post("/auth/login", json={
        "email": email_b,
        "password": "Password123!"
    })
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 4. Create Diagnostic Centre
    log_step(4, "Create Diagnostic Centre")
    centre_resp = client.post("/centres/", json={
        "name": "Manipal Diagnostics Hub",
        "location": "Old Airport Road, Bengaluru"
    })
    assert centre_resp.status_code == 201, f"Create centre failed: {centre_resp.text}"
    centre_id = centre_resp.json()["id"]
    print(f"Centre created: {centre_id} - {centre_resp.json()['name']}")

    # 5. Create Diagnostic Test
    log_step(5, "Create Diagnostic Test")
    test_resp = client.post(f"/centres/{centre_id}/tests", json={
        "name": "Thyroid Profile (T3, T4, TSH)",
        "description": "Comprehensive thyroid function evaluation",
        "price": "750.00"
    })
    assert test_resp.status_code == 201, f"Create test failed: {test_resp.text}"
    test_id = test_resp.json()["id"]
    print(f"Test created: {test_id} - Price: Rs. {test_resp.json()['price']}")

    # 6. Create Booking
    log_step(6, "Create Booking")
    booking_resp = client.post("/bookings/", json={
        "diagnostic_centre_id": centre_id,
        "diagnostic_test_id": test_id,
        "appointment_datetime": datetime.now(timezone.utc).isoformat()
    }, headers=headers_a)
    assert booking_resp.status_code == 201, f"Create booking failed: {booking_resp.text}"
    booking_a = booking_resp.json()
    booking_id = booking_a["id"]
    assert booking_a["status"] == "PENDING"
    assert float(booking_a["amount"]) == 750.0
    print(f"Booking created: {booking_id} - Status: {booking_a['status']} - Amount: {booking_a['amount']}")

    # 7. Process Simulated Payment (PENDING -> initiated)
    log_step(7, "Process Simulated Payment")
    pay_init = client.post("/payments/", json={
        "booking_id": booking_id,
        "simulated_status": "PENDING"
    }, headers=headers_a)
    assert pay_init.status_code == 201, f"Initiate payment failed: {pay_init.text}"
    provider_ref = pay_init.json()["provider_reference"]
    print(f"Payment initiated: Provider Ref = {provider_ref}")

    # 8. Confirm Booking via Webhook
    log_step(8, "Confirm Booking via Webhook")
    event_id = f"evt_live_{uuid.uuid4().hex}"
    webhook_resp = client.post("/payments/webhook/", json={
        "event_id": event_id,
        "payment_reference": provider_ref,
        "status": "SUCCESS",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    assert webhook_resp.status_code == 200, f"Webhook failed: {webhook_resp.text}"
    assert webhook_resp.json()["status"] == "processed"
    print(f"Webhook delivered successfully: status = {webhook_resp.json()['status']}")

    # Check booking state
    check_booking = client.get(f"/bookings/{booking_id}", headers=headers_a)
    assert check_booking.json()["status"] == "CONFIRMED"
    print(f"Verified booking status: {check_booking.json()['status']}")

    # 9. Send identical webhook again (Idempotency)
    log_step(9, "Send identical webhook again (2nd time)")
    dup_resp1 = client.post("/payments/webhook/", json={
        "event_id": event_id,
        "payment_reference": provider_ref,
        "status": "SUCCESS",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    assert dup_resp1.status_code == 200
    assert dup_resp1.json()["status"] == "already_processed"
    print("2nd delivery acknowledged idempotently without error.")

    # 10. Send identical webhook multiple times (Repeated retries)
    log_step(10, "Send identical webhook multiple times (3rd, 4th, 5th time)")
    for i in range(3, 6):
        dup_resp = client.post("/payments/webhook/", json={
            "event_id": event_id,
            "payment_reference": provider_ref,
            "status": "SUCCESS"
        })
        assert dup_resp.status_code == 200
        assert dup_resp.json()["status"] == "already_processed"
    print("Repeated webhook deliveries safely handled as idempotent.")

    # 11. Verify no duplicate payment
    log_step(11, "Verify no duplicate payment")
    # Attempt second payment on confirmed booking
    dup_pay = client.post("/payments/", json={
        "booking_id": booking_id,
        "simulated_status": "SUCCESS"
    }, headers=headers_a)
    assert dup_pay.status_code == 400
    print("Duplicate payment blocked by state machine (HTTP 400).")

    # 12. Verify no duplicate booking & booking state unchanged
    log_step(12, "Verify booking state remains correctly CONFIRMED")
    final_booking_check = client.get(f"/bookings/{booking_id}", headers=headers_a)
    assert final_booking_check.json()["status"] == "CONFIRMED"
    print("Booking state remains strictly CONFIRMED.")

    # 13. Test unauthorized booking access (IDOR)
    log_step(13, "Test unauthorized booking access (IDOR)")
    unauth_get = client.get(f"/bookings/{booking_id}", headers=headers_b)
    assert unauth_get.status_code == 403, f"Expected 403, got {unauth_get.status_code}"
    print("User B blocked from viewing User A's booking (HTTP 403 Forbidden).")

    unauth_cancel = client.post(f"/bookings/{booking_id}/cancel", headers=headers_b)
    assert unauth_cancel.status_code == 403
    print("User B blocked from cancelling User A's booking (HTTP 403 Forbidden).")

    # 14. Test Cancellation on a separate PENDING booking
    log_step(14, "Test booking cancellation")
    booking_to_cancel_resp = client.post("/bookings/", json={
        "diagnostic_centre_id": centre_id,
        "diagnostic_test_id": test_id,
        "appointment_datetime": datetime.now(timezone.utc).isoformat()
    }, headers=headers_a)
    cancel_booking_id = booking_to_cancel_resp.json()["id"]

    cancel_action = client.post(f"/bookings/{cancel_booking_id}/cancel", headers=headers_a)
    assert cancel_action.status_code == 200
    assert cancel_action.json()["status"] == "CANCELLED"
    print(f"Booking {cancel_booking_id} successfully cancelled.")

    # Cancelling again must fail
    second_cancel = client.post(f"/bookings/{cancel_booking_id}/cancel", headers=headers_a)
    assert second_cancel.status_code == 400
    print("Cancelling already cancelled booking rejected (HTTP 400).")

    # 15. Test Rate Limiting
    log_step(15, "Test Rate Limiting")
    hit_limit = False
    for i in range(15):
        rl_resp = client.post("/auth/login", json={
            "email": "spam@example.com",
            "password": "WrongPassword!"
        })
        if rl_resp.status_code == 429:
            hit_limit = True
            print(f"Rate limiter triggered on request {i+1} with HTTP 429: {rl_resp.json()['detail']}")
            break
    assert hit_limit, "Rate limiter did not trigger as expected"

    print("\n============================================================")
    print("ALL 17 VERIFICATION STEPS PASSED SUCCESSFULLY ON LIVE SERVER!")
    print("============================================================")

if __name__ == "__main__":
    main()
