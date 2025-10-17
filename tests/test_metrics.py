from __future__ import annotations

from fastapi.testclient import TestClient

from python_mastery_portfolio.api import app


def test_metrics_endpoint_without_prometheus() -> None:
    client = TestClient(app)
    r = client.get("/metrics")
    assert r.status_code == 200
    # Either empty or valid exposition format; we at least check content-type presence
    assert "content-type" in {k.lower(): v for k, v in r.headers.items()}
