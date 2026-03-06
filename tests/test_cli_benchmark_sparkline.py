from __future__ import annotations

from typer.testing import CliRunner

from python_mastery_portfolio.cli import app


def test_benchmark_sparkline_outputs():
    runner = CliRunner()
    # run a small benchmark with reduced iterations via n=5 and iterations=3 by calling benchmark with options
    res = runner.invoke(app, ["benchmark", "--n", "5", "--iterations", "3", "--sparkline"])
    assert res.exit_code == 0
    out = res.stdout
    assert "iterative" in out or "fast" in out
    # sparkline should produce a block character or similar
    assert "█" in out or "#" in out

