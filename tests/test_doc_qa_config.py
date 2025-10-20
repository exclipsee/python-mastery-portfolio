from __future__ import annotations

from fastapi.testclient import TestClient

from python_mastery_portfolio.api import app


def test_config_simple_naive() -> None:
    client = TestClient(app)
    r = client.post("/qa/config", params={"embedder": "simple", "index": "naive"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"


def test_config_raises_on_unknown() -> None:
    client = TestClient(app)
    r = client.post("/qa/config", params={"embedder": "bad", "index": "naive"})
    assert r.status_code == 400
