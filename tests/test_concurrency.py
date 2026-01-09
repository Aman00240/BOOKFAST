import pytest
import httpx
import asyncio

BASE_URL = "http://localhost:8000"
EMAIL = "tester@example.com"
PASSWORD = "testpassword1"


@pytest.mark.asyncio
async def test_race_condition():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        await client.post("/register", json={"email": EMAIL, "password": PASSWORD})

        login_res = await client.post(
            "/login", data={"username": EMAIL, "password": PASSWORD}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        event_res = await client.post(
            "/events",
            json={
                "event_name": "Race Condition Test",
                "date": "2030-02-02T00:00:00",
                "ticket_price": 10.0,
                "total_tickets": 1,
            },
            headers=headers,
        )

        event_id = event_res.json()["id"]

        tasks = []
        for _ in range(10):
            tasks.append(
                client.post("/book", json={"event_id": event_id}, headers=headers)
            )

        print(f"Sending 10 concurrent requests for Event {event_id}...")
        response = await asyncio.gather(*tasks)

        success_count = 0
        sold_out_count = 0

        for r in response:
            if r.status_code == 200:
                success_count += 1
            elif r.status_code == 400 and "Sold Out" in r.text:
                sold_out_count += 1

        print(f"Success: {success_count}")
        print(f"Sold out errors: {sold_out_count}")

        assert success_count == 1
        assert sold_out_count == 9
