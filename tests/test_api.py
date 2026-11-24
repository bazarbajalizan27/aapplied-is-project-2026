from fastapi.testclient import TestClient
from app.main import app


def test_get_items():
    with TestClient(app) as client:
        r = client.get("/items")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


def test_create_item():
    with TestClient(app) as client:
        r = client.post("/items", json={"name": "Test", "price": 10.5, "category_id": 1})
        assert r.status_code == 201
        assert r.json()["name"] == "Test"


def test_negative_price():
    with TestClient(app) as client:
        r = client.post("/items", json={"name": "Bad", "price": -5, "category_id": 1})
        assert r.status_code == 422