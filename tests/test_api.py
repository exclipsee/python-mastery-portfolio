from __future__ import annotations

from fastapi.testclient import TestClient

from python_mastery_portfolio.api import app


def test_fib_endpoint() -> None:
    client = TestClient(app)
    r = client.get("/fib/10")
    assert r.status_code == 200
    data = r.json()
    assert data["n"] == 10
    assert data["value"] == 55


def test_fib_endpoint_negative() -> None:
    client = TestClient(app)
    r = client.get("/fib/-3")
    assert r.status_code == 200
    data = r.json()
    assert data["n"] == 0
    assert data["value"] == 0


def test_vin_validate_api() -> None:
    client = TestClient(app)
    r = client.post("/vin/validate", json={"vin": "1HGCM82633A004352"})
    assert r.status_code == 200
    data = r.json()
    assert data == {"vin": "1HGCM82633A004352", "valid": True}
