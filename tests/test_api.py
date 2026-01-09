import pytest
import httpx
import uuid

BASE_URL = "http://localhost:8000"


def generate_id():
    return str(uuid.uuid4())


@pytest.mark.asyncio
async def test_1_auth_flow():
    email = f"user_{generate_id()}@test.com"
    password = "password12"

    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        reg_res = await client.post(
            "/register", json={"email": email, "password": password}
        )
        assert reg_res.status_code == 200
        assert reg_res.json()["email"] == email

        login_res = await client.post(
            "/login", data={"username": email, "password": password}
        )
        assert login_res.status_code == 200
        data = login_res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_2_event_lifecycle():
    email = f"admin_{generate_id()}@test.com"
    password = "password123"

    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        await client.post("/register", json={"email": email, "password": password})
        token = (
            await client.post("/login", data={"username": email, "password": password})
        ).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        event_data = {
            "event_name": "Test Festival",
            "date": "2030-01-01T10:00:00",
            "ticket_price": 50.0,
            "total_tickets": 100,
        }

        res = await client.post("/events", json=event_data, headers=headers)
        assert res.status_code == 200
        event_id = res.json()["id"]

        update_data = {"event_name": "Updated Event", "ticket_price": 75.0}
        res = await client.patch(
            f"events/{event_id}", json=update_data, headers=headers
        )
        assert res.status_code == 200
        assert res.json()["event_name"] == "Updated Event"

        res = await client.delete(f"/events/{event_id}", headers=headers)
        assert res.status_code == 204

        res = await client.get(f"event/{event_id}")
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_3_booking_and_cancellation():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        email = f"buyer_{generate_id()}@test.com"
        await client.post("/register", json={"email": email, "password": "password12"})
        token = (
            await client.post(
                "/login", data={"username": email, "password": "password12"}
            )
        ).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        event_res = await client.post(
            "/events",
            json={
                "event_name": "Booking Test",
                "date": "2030-05-05T00:00:00",
                "ticket_price": 10,
                "total_tickets": 10,
            },
            headers=headers,
        )
        event_id = event_res.json()["id"]

        book_res = await client.post(
            "/book", json={"event_id": event_id}, headers=headers
        )
        assert book_res.status_code == 200
        ticket_id = book_res.json()["id"]

        e_check = await client.get(f"/event/{event_id}")
        assert e_check.json()["tickets_sold"] == 1

        cancel_res = await client.post(f"/tickets/{ticket_id}/cancel", headers=headers)
        assert cancel_res.status_code == 200, cancel_res.text
        assert cancel_res.json()["status"] == "cancelled"

        e_check = await client.get(f"/event/{event_id}")
        assert e_check.json()["tickets_sold"] == 0
