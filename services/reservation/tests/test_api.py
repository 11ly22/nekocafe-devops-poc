from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["service"] == "reservation"


def test_create_reservation():
    r = client.post(
        "/api/v1/reservations",
        json={
            "store_id": "BJ-001",
            "date": "2026-05-15",
            "time_slot": "14:00",
            "cat_count": 2,
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "pending"
    assert data["store_id"] == "BJ-001"


def test_get_availability():
    r = client.get("/api/v1/stores/BJ-001/availability")
    assert r.status_code == 200
    assert len(r.json()["slots"]) >= 1
