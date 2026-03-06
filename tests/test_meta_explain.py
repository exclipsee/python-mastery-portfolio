from __future__ import annotations

from fastapi.testclient import TestClient

from python_mastery_portfolio.api import app


def test_meta_explain_for_fibonacci():
    client = TestClient(app)
    r = client.get("/meta/explain?fn=fibonacci")
    assert r.status_code == 200
    data = r.json()
    assert data.get("fn") == "fibonacci"
    assert "signature" in data
    assert "doc" in data
    assert isinstance(data.get("summary"), str)


def test_meta_explain_not_found():
    client = TestClient(app)
    r = client.get("/meta/explain?fn=nonexistent_fn_123")
    assert r.status_code == 200
    data = r.json()
    assert "error" in data
    assert data["error"] == "function not found"

