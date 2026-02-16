from __future__ import annotations

from typer.testing import CliRunner

from python_mastery_portfolio import __version__
from python_mastery_portfolio.cli import app


def test_cli_version() -> None:
    runner = CliRunner()
    res = runner.invoke(app, ["version"])
    assert res.exit_code == 0
    assert __version__ in res.stdout.strip()

