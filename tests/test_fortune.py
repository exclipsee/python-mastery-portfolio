from __future__ import annotations

from fastapi.testclient import TestClient

from python_mastery_portfolio.api import app


def test_fortune_seed_reproducible():
    client = TestClient(app)
    r1 = client.get("/fortune?seed=42")
    r2 = client.get("/fortune?seed=42")
    assert r1.status_code == 200
    assert r1.json() == r2.json()
    assert "fortune" in r1.json()


def test_fortune_random():
    client = TestClient(app)
    r = client.get("/fortune")
    assert r.status_code == 200
    data = r.json()
    assert "fortune" in data and "index" in data

