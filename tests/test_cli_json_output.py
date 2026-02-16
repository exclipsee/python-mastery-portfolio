from __future__ import annotations

from typer.testing import CliRunner

from python_mastery_portfolio.cli import app


def test_fib_cli_json_output():
    runner = CliRunner()
    res = runner.invoke(app, ["fib", "5", "--json"])
    assert res.exit_code == 0
    assert "\"n\"" in res.stdout and "\"value\"" in res.stdout

