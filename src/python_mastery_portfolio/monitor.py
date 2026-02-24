"""Lightweight monitoring utilities.

Includes URL pinging with optional Prometheus histogram observation and a
simple Slack webhook sender used for notifications in examples/tests.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
try:
    from prometheus_client import Histogram  # type: ignore
except Exception:  # pragma: no cover - optional
    Histogram = None  # type: ignore

from typing import Any

# Create a histogram instance only if the dependency is available.
if Histogram is not None:
    PING_HISTOGRAM: Any = Histogram(
        "monitor_ping_duration_seconds", "Latency for URL ping requests", ["target"]
    )
else:
    PING_HISTOGRAM: Any = None


@dataclass
class PingResult:
    url: str
    ok: bool
    status: int | None
    seconds: float


def ping_url(url: str, timeout: float = 5.0) -> PingResult:
    """Ping a URL and return status, success flag and elapsed seconds."""
    start = time.perf_counter()
    status: int | None = None
    ok = False
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            status = getattr(resp, "status", None) or resp.getcode()
            ok = 200 <= (status or 0) < 400
    except urllib.error.HTTPError as e:  # HTTP error response
        status = e.code
        ok = False
    except Exception:
        ok = False
    elapsed = time.perf_counter() - start
    if PING_HISTOGRAM is not None:
        PING_HISTOGRAM.labels(url).observe(elapsed)
    return PingResult(url=url, ok=ok, status=status, seconds=elapsed)


def send_slack_webhook(webhook_url: str, text: str, timeout: float = 5.0) -> bool:
    """Send a simple text message to a Slack incoming webhook URL."""
    data = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = getattr(resp, "status", None) or resp.getcode()
            return 200 <= (code or 0) < 300
    except Exception:
        return False
