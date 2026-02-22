from __future__ import annotations

from fastapi.testclient import TestClient

from python_mastery_portfolio.api import app


def test_reproduce_curl_header_present_on_get():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert "X-Reproduce-Curl" in r.headers
    assert r.headers["X-Reproduce-Curl"].startswith("curl -X GET")


def test_reproduce_curl_header_contains_path():
    client = TestClient(app)
    r = client.get("/fib/5")
    assert r.status_code == 200
    header = r.headers.get("X-Reproduce-Curl", "")
    assert "/fib/5" in header

