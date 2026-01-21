from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from python_mastery_portfolio.cli import app


def test_cli_fib() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["fib", "10"])
    assert result.exit_code == 0
    assert result.output.strip() == "55"


def test_cli_search_found() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["search", "--value", "42", "1", "2", "42", "100"])  # sorted list
    assert result.exit_code == 0
    assert "Found 42 at index" in result.output


def test_cli_search_not_found() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["search", "--value", "7", "1", "2", "3"])  # not present
    assert result.exit_code != 0


def test_cli_vin_check_invalid_length() -> None:
    runner = CliRunner()
    res = runner.invoke(app, ["vin-check", "SHORTVIN"])
    assert res.exit_code != 0


def test_cli_ml_train_and_predict_with_model(tmp_path_factory: object) -> None:
    runner = CliRunner()
    tmp_dir = tmp_path_factory.mktemp("cli-model")  # type: ignore[attr-defined]
    model_path = tmp_dir / "linreg.joblib"

    # Train and save a model
    res_train = runner.invoke(
        app,
        [
            "ml-train",
            "--y",
            "3",
            "--y",
            "6",
            "--y",
            "9",
            "--save",
            str(model_path),
            "--add-bias",
            "1,2",
            "2,4",
            "3,6",
        ],
    )
    assert res_train.exit_code == 0
    assert Path(res_train.output.strip()).exists()

    # Predict using the saved model
    res_pred = runner.invoke(
        app,
        [
            "ml-predict",
            "--model",
            str(model_path),
            "--add-bias",
            "1,2",
            "2,4",
            "3,6",
        ],
    )
    assert res_pred.exit_code == 0
    out_vals = [float(v) for v in res_pred.output.strip().split(",")]
    assert len(out_vals) == 3


def test_cli_ml_train_print_coef() -> None:
    runner = CliRunner()
    res = runner.invoke(
        app,
        [
            "ml-train",
            "--y",
            "2",
            "--y",
            "4",
            "--y",
            "6",
            "1,1",
            "2,2",
            "3,3",
        ],
    )
    assert res.exit_code == 0
    # Output should be comma-separated coefficients
    parts = res.output.strip().split(",")
    assert all(part.strip() for part in parts)


def test_cli_ml_predict_with_coef() -> None:
    runner = CliRunner()
    res = runner.invoke(
        app,
        [
            "ml-predict",
            "--coef",
            "1",
            "--coef",
            "2",
            "1,2",
            "0,1",
        ],
    )
    assert res.exit_code == 0
    vals = [float(v) for v in res.output.strip().split(",")]
    assert len(vals) == 2


def test_cli_gcd() -> None:
    runner = CliRunner()
    res = runner.invoke(app, ["gcd", "48", "18"])
    assert res.exit_code == 0
    assert res.output.strip() == "6"


def test_cli_benchmark_iterative_and_fast_json() -> None:
    runner = CliRunner()
    # run a tiny benchmark to keep tests fast
    res = runner.invoke(
        app, ["benchmark", "--n", "10", "--iterations", "10", "--warmup", "1", "--json"]
    )
    assert res.exit_code == 0
    out = json.loads(res.output)
    assert "iterative" in out or "fast" in out
