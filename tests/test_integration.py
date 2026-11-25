from fastapi.testclient import TestClient
from app.main import app


def test_crud_flow():
    with TestClient(app) as c:
        r = c.post("/items", json={"name": "IntegrationItem", "price": 100, "category_id": 1})
        assert r.status_code == 201
        item_id = r.json()["id"]
        assert c.get(f"/items/{item_id}").status_code == 200
        r = c.patch(f"/items/{item_id}", json={"price": 150})
        assert r.status_code == 200
        assert r.json()["price"] == 150
        assert c.delete(f"/items/{item_id}").status_code in (200, 204)
        assert c.get(f"/items/{item_id}").status_code == 404


def test_not_found():
    with TestClient(app) as c:
        assert c.get("/items/999999").status_code == 404
        assert c.patch("/items/999999", json={"price": 1}).status_code == 404
        assert c.delete("/items/999999").status_code == 404


def test_search_filter():
    with TestClient(app) as c:
        r = c.get("/items", params={"search": "Laptop"})
        assert r.status_code == 200
        assert isinstance(r.json(), list)