from __future__ import annotations

from time import monotonic

from fastapi.testclient import TestClient

from python_mastery_portfolio import __version__
from python_mastery_portfolio.api import app


def test_health_endpoint() -> None:
    client = TestClient(app)
    start = monotonic()
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"
    assert "uptime" in data
    assert isinstance(data["uptime"], float)
    assert data["uptime"] >= 0.0
    assert data.get("version") == __version__
    # uptime should be reasonably small (not negative)
    assert data["uptime"] >= 0.0
    assert data["uptime"] <= (monotonic() - start) + 1.0

