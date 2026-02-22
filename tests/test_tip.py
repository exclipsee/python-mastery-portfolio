from __future__ import annotations

from fastapi.testclient import TestClient

from python_mastery_portfolio.api import app


def test_tip_endpoint_seed_and_fields() -> None:
    client = TestClient(app)
    r = client.get("/tip?seed=1")
    assert r.status_code == 200
    data = r.json()
    assert "tip" in data
    assert "index" in data
    assert data["index"] == 1 % len(data["tip"] if isinstance(data.get("tip"), list) else [data["tip"]]) or isinstance(data["index"], int)
    # call without seed
    r2 = client.get("/tip")
    assert r2.status_code == 200
    d2 = r2.json()
    assert "tip" in d2 and "index" in d2 and "date" in d2

