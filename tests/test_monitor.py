from __future__ import annotations

from typing import Any
from unittest import mock

from typer.testing import CliRunner

from python_mastery_portfolio.cli import app
from python_mastery_portfolio.monitor import PingResult, ping_url, send_slack_webhook


def test_ping_url_ok(monkeypatch: Any) -> None:
    class Resp:
        def __init__(self) -> None:
            self.status = 200

        def getcode(self) -> int:
            return 200

        def __enter__(self) -> Resp:
            return self

        def __exit__(self, *args: Any) -> None:
            return None

    def fake_urlopen(url: str, timeout: float = 5.0) -> Resp:
        return Resp()

    with mock.patch("urllib.request.urlopen", fake_urlopen):
        res = ping_url("http://example.com")
        assert isinstance(res, PingResult)
        assert res.ok and res.status == 200


def test_send_slack_webhook_ok(monkeypatch: Any) -> None:
    class Resp:
        def __init__(self) -> None:
            self.status = 200

        def getcode(self) -> int:
            return 200

        def __enter__(self) -> Resp:
            return self

        def __exit__(self, *args: Any) -> None:
            return None

    def fake_urlopen(req: Any, timeout: float = 5.0) -> Resp:
        return Resp()

    with mock.patch("urllib.request.urlopen", fake_urlopen):
        ok = send_slack_webhook("http://example.com/webhook", "hello")
        assert ok is True


def test_ping_url_fail(monkeypatch: Any) -> None:
    def fake_urlopen(url: str, timeout: float = 5.0) -> object:
        raise OSError("network down")

    with mock.patch("urllib.request.urlopen", fake_urlopen):
        res = ping_url("http://localhost")
        assert res.ok is False


def test_cli_monitor_ping(monkeypatch: Any) -> None:
    class Resp:
        def __init__(self, status: int) -> None:
            self.status = status

        def getcode(self) -> int:
            return self.status

        def __enter__(self) -> Resp:
            return self

        def __exit__(self, *args: Any) -> None:
            return None

    def fake_urlopen(url: str, timeout: float = 5.0) -> object:
        return Resp(204)

    with mock.patch("urllib.request.urlopen", fake_urlopen):
        runner = CliRunner()
        res = runner.invoke(app, ["monitor-ping", "http://localhost:8000/health"])
        assert res.exit_code == 0
