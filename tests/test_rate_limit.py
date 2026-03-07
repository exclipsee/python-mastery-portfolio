from __future__ import annotations

from fastapi.testclient import TestClient

from python_mastery_portfolio import api


def test_rate_limit_exceeded(monkeypatch) -> None:
    # Replace the module-level _check_rate_limit with a wrapper that uses a tiny max
    orig = api._check_rate_limit

    def limited(req, max_req: int = 2):
        return orig(req, max_req=2)

    monkeypatch.setattr(api, "_check_rate_limit", limited)
    # Clear any existing buckets
    api._rate_buckets.clear()

    client = TestClient(api.app)
    body = {"vin": "1HGCM82633A004352"}
    # Two requests should pass
    r1 = client.post("/vin/validate", json=body)
    assert r1.status_code == 200
    r2 = client.post("/vin/validate", json=body)
    assert r2.status_code == 200
    # Third should be rate-limited
    r3 = client.post("/vin/validate", json=body)
    assert r3.status_code == 429

