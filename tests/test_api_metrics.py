from __future__ import annotations

from fastapi.testclient import TestClient

from python_mastery_portfolio.api import app


def test_stats_endpoint_and_counters() -> None:
    client = TestClient(app)
    # call a couple endpoints
    r1 = client.get("/fib/3")
    assert r1.status_code == 200
    r2 = client.get("/health")
    assert r2.status_code == 200

    resp = client.get("/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"
    counters = data.get("counters", {})
    # Expect at least fib and health paths to be present
    assert "/fib/3" in counters or any(k.startswith("/fib/") for k in counters.keys())
    assert "/health" in counters

