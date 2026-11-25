from fastapi.testclient import TestClient
from app.main import app


def test_sql_injection_in_search():
    with TestClient(app) as c:
        r = c.get("/items", params={"search": "' OR '1'='1"})
        assert r.status_code == 200
        r = c.get("/items", params={"search": "'; DROP TABLE item; --"})
        assert r.status_code == 200
        assert c.get("/items").status_code == 200


def test_invalid_price_rejected():
    with TestClient(app) as c:
        r = c.post("/items", json={"name": "Bad", "price": -1, "category_id": 1})
        assert r.status_code == 422


def test_wrong_types_rejected():
    with TestClient(app) as c:
        r = c.post("/items", json={"name": "Bad", "price": "abc", "category_id": 1})
        assert r.status_code == 422