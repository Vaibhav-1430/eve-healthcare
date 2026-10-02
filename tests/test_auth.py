import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    response = await client.post(
        "/auth/signup",
        json={
            "email": "doctor@evehealthcare.com",
            "password": "SecurePassword123!",
            "full_name": "Dr. Sarah Connor",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "doctor@evehealthcare.com"
    assert data["full_name"] == "Dr. Sarah Connor"
    assert "id" in data
    # Password and hash must never be returned in API response
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_duplicate_signup(client: AsyncClient):
    payload = {
        "email": "duplicate@evehealthcare.com",
        "password": "SecurePassword123!",
        "full_name": "John Doe",
    }
    first_resp = await client.post("/auth/signup", json=payload)
    assert first_resp.status_code == 201

    second_resp = await client.post("/auth/signup", json=payload)
    assert second_resp.status_code == 400
    assert "already exists" in second_resp.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    # Create user first
    await client.post(
        "/auth/signup",
        json={
            "email": "loginuser@evehealthcare.com",
            "password": "MyPassword123!",
            "full_name": "Login User",
        },
    )

    response = await client.post(
        "/auth/login",
        json={"email": "loginuser@evehealthcare.com", "password": "MyPassword123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "loginuser@evehealthcare.com"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    await client.post(
        "/auth/signup",
        json={
            "email": "invalidpass@evehealthcare.com",
            "password": "CorrectPassword123!",
            "full_name": "Valid User",
        },
    )

    response = await client.post(
        "/auth/login",
        json={"email": "invalidpass@evehealthcare.com", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_protected_route_without_token(client: AsyncClient):
    response = await client.get("/bookings/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_signup_malformed_request(client: AsyncClient):
    # Missing required password and invalid email
    response = await client.post(
        "/auth/signup",
        json={"email": "not-an-email"},
    )
    assert response.status_code == 422
