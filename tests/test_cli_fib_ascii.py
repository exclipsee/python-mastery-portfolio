from __future__ import annotations

from typer.testing import CliRunner

from python_mastery_portfolio.cli import app


def test_fib_ascii_output_contains_bars() -> None:
    runner = CliRunner()
    res = runner.invoke(app, ["fib", "6", "--ascii"])
    assert res.exit_code == 0
    out = res.stdout
    # should contain at least one bar character or dot marker
    assert "█" in out or "#" in out or "." in out
    # ensure lines for indices 0..6 appear
    for i in range(7):
        assert f"{i}:" in out

