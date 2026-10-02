import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_centre(client: AsyncClient):
    response = await client.post(
        "/centres/",
        json={"name": "Max Healthcare", "location": "Saket, New Delhi"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Max Healthcare"
    assert data["location"] == "Saket, New Delhi"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_centres_and_pagination(client: AsyncClient):
    for i in range(5):
        await client.post(
            "/centres/",
            json={"name": f"Centre {i}", "location": f"City {i}"},
        )

    response = await client.get("/centres/?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] == 5
    assert data["pages"] == 3


@pytest.mark.asyncio
async def test_get_centre_by_id(client: AsyncClient):
    create_resp = await client.post(
        "/centres/",
        json={"name": "Fortis Diagnostic", "location": "Sector 62, Noida"},
    )
    centre_id = create_resp.json()["id"]

    response = await client.get(f"/centres/{centre_id}")
    assert response.status_code == 200
    assert response.json()["id"] == centre_id
    assert response.json()["name"] == "Fortis Diagnostic"


@pytest.mark.asyncio
async def test_get_centre_invalid_id(client: AsyncClient):
    non_existent_id = uuid.uuid4()
    response = await client.get(f"/centres/{non_existent_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_test_and_list_by_centre(client: AsyncClient):
    centre_resp = await client.post(
        "/centres/",
        json={"name": "SRL Diagnostics", "location": "Koramangala, Bengaluru"},
    )
    centre_id = centre_resp.json()["id"]

    test_resp = await client.post(
        f"/centres/{centre_id}/tests",
        json={
            "name": "Lipid Profile",
            "description": "Cholesterol and triglyceride levels",
            "price": "650.00",
        },
    )
    assert test_resp.status_code == 201
    test_data = test_resp.json()
    assert test_data["name"] == "Lipid Profile"
    assert float(test_data["price"]) == 650.0
    assert test_data["centre_id"] == centre_id

    # List tests for centre
    list_resp = await client.get(f"/centres/{centre_id}/tests?page=1&page_size=10")
    assert list_resp.status_code == 200
    assert len(list_resp.json()["items"]) == 1


@pytest.mark.asyncio
async def test_create_test_for_invalid_centre(client: AsyncClient):
    invalid_centre_id = uuid.uuid4()
    response = await client.post(
        f"/centres/{invalid_centre_id}/tests",
        json={"name": "HbA1c", "price": "450.00"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_test_with_negative_price(client: AsyncClient):
    centre_resp = await client.post(
        "/centres/",
        json={"name": "Centre Test", "location": "Mumbai"},
    )
    centre_id = centre_resp.json()["id"]

    response = await client.post(
        f"/centres/{centre_id}/tests",
        json={"name": "Invalid Test", "price": "-10.00"},
    )
    assert response.status_code == 422
