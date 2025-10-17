from __future__ import annotations

import typer

from .algorithms import binary_search, fibonacci
from .excel_tools import write_rows_to_excel
from .ml_pipeline import (
    add_bias_feature,
    load_model,
    predict,
    save_model,
    train_linear_regression,
)
from .monitor import ping_url, send_slack_webhook
from .vin import compute_check_digit, is_valid_vin

app = typer.Typer(help="Python Mastery Portfolio CLI")


@app.command()
def fib(
    n: int = typer.Argument(..., min=0, help="Return the n-th Fibonacci number (0-indexed)"),
) -> None:
    """Compute the n-th Fibonacci number."""
    typer.echo(fibonacci(n))


@app.command("search")
def search_command(
    value: int = typer.Option(..., "--value", help="Value to search for"),
    items: list[int] = typer.Argument(
        ..., help="Sorted list of integers to search", metavar="ITEMS..."
    ),
) -> None:
    """Binary search for VALUE in a sorted list of IN items."""
    idx = binary_search(items, value)
    if idx >= 0:
        typer.echo(f"Found {value} at index {idx}")
    else:
        raise typer.Exit(code=1)


def main() -> None:  # pragma: no cover
    app()


@app.command("vin-validate")
def vin_validate(vin: str = typer.Argument(..., help="17-character VIN")) -> None:
    """Validate a VIN using ISO 3779 (check digit)."""
    typer.echo("valid" if is_valid_vin(vin) else "invalid")


@app.command("vin-check")
def vin_check(vin: str = typer.Argument(..., help="17-character VIN")) -> None:
    """Print the computed check digit for a VIN."""
    vin_u = vin.upper()
    if len(vin_u) != 17:
        raise typer.Exit(code=2)
    typer.echo(compute_check_digit(vin_u))


@app.command("excel-export")
def excel_export(
    output: str = typer.Option("output.xlsx", "--output", help="Path to save .xlsx"),
    rows: list[str] = typer.Argument(
        ..., help="Rows as CSV-like strings, e.g. 'col1,col2' 'v1,v2'"
    ),
) -> None:
    """Create a simple Excel file from provided CSV-like rows.

    Example:
      pm-portfolio excel-export --output report.xlsx "Name,Score" "Alice,90" "Bob,88"
    """
    parsed = [r.split(",") for r in rows]
    path = write_rows_to_excel(parsed, output)
    typer.echo(str(path))


@app.command("ml-train")
def ml_train(
    y: list[float] = typer.Option(..., "--y", help="Target values, e.g. --y 1 2 3"),
    x: list[str] = typer.Argument(..., help="Feature rows as 'v1,v2,...' e.g. '1,2' '3,4'"),
    save: str | None = typer.Option(None, "--save", help="Optional path to save trained model"),
    add_bias: bool = typer.Option(
        False, "--add-bias", help="Prepend a bias feature (1.0) to each row"
    ),
) -> None:
    rows = [[float(v) for v in r.split(",")] for r in x]
    if add_bias:
        rows = add_bias_feature(rows)
    model = train_linear_regression(rows, y)
    if save:
        path = save_model(model, save)
        typer.echo(str(path))
    else:
        # Print fitted coefficients for demonstration
        typer.echo(",".join(map(str, model.model.coef_.tolist())))


@app.command("ml-predict")
def ml_predict(
    coef: list[float] | None = typer.Option(
        None, "--coef", help="Model coefficients (ignored if --model is provided)"
    ),
    rows: list[str] = typer.Argument(..., help="Rows as 'v1,v2,...'"),
    model: str | None = typer.Option(
        None, "--model", help="Path to a saved model (created by ml-train --save)"
    ),
    add_bias: bool = typer.Option(
        False, "--add-bias", help="Prepend a bias feature (1.0) to each row"
    ),
) -> None:
    x_rows = [[float(v) for v in r.split(",")] for r in rows]
    if add_bias:
        x_rows = add_bias_feature(x_rows)

    if model:
        tm = load_model(model)
        preds = predict(tm, x_rows)
    else:
        if coef is None:
            raise typer.BadParameter("Provide --coef or --model")
        # For demo purpose, we retrain a tiny model with synthetic y derived from coef
        y_vals = [sum(c * xi for c, xi in zip(coef, row, strict=True)) for row in x_rows]
        tm = train_linear_regression(x_rows, y_vals)
        preds = predict(tm, x_rows)
    typer.echo(",".join(f"{p:.3f}" for p in preds))


@app.command("monitor-ping")
def monitor_ping_cmd(
    url: str = typer.Argument(
        ..., help="URL to ping, e.g. http://localhost:8000/health"
    ),
    iterations: int = typer.Option(
        1, "--iterations", "-n", min=1, help="Number of pings"
    ),
    interval: float = typer.Option(
        0.5, "--interval", "-i", min=0.0, help="Sleep between pings (s)"
    ),
    slack_webhook: str | None = typer.Option(
        None, "--slack-webhook", help="Slack incoming webhook URL for alerts"
    ),
) -> None:
    import time as _t

    worst: float | None = None
    for _ in range(iterations):
        res = ping_url(url)
        typer.echo(f"{res.status} in {res.seconds:.3f}s -> {'OK' if res.ok else 'FAIL'}")
        worst = res.seconds if worst is None else max(worst, res.seconds)
        if not res.ok and slack_webhook:
            send_slack_webhook(slack_webhook, f"Ping failed: {url} (status={res.status})")
        if iterations > 1:
            _t.sleep(interval)
    if worst is not None:
        typer.echo(f"worst={worst:.3f}s")
