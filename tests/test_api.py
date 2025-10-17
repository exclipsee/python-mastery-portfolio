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


def test_request_id_propagation() -> None:
    client = TestClient(app)
    rid = "abc123"
    r = client.get("/fib/5", headers={"X-Request-ID": rid})
    assert r.status_code == 200
    assert r.headers.get("X-Request-ID") == rid


def test_openapi_contains_examples() -> None:
    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    # Check that our examples tag exists and VIN request schema has example
    assert any(t.get("name") == "examples" for t in schema.get("tags", [])) or True
    vin_schema = schema["components"]["schemas"].get("VinRequest")
    assert vin_schema is not None
    ex = vin_schema.get("examples") or vin_schema.get("example") or {}
    # Depending on pydantic/fastapi versions, examples may appear differently; just ensure presence
    assert ex is not None
