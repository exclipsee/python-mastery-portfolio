from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for typing
    from prometheus_client import Histogram
else:
    try:  # pragma: no cover - runtime optional import
        from prometheus_client import Histogram  # type: ignore
    except Exception:  # pragma: no cover
        Histogram = None  # type: ignore


PING_HISTOGRAM: Histogram | None
if 'Histogram' in globals() and Histogram is not None:
    PING_HISTOGRAM = Histogram(
        "monitor_ping_duration_seconds",
        "Latency for URL ping requests",
        ["target"],
    )
else:
    PING_HISTOGRAM = None


@dataclass
class PingResult:
    url: str
    ok: bool
    status: int | None
    seconds: float


def ping_url(url: str, timeout: float = 5.0) -> PingResult:
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
