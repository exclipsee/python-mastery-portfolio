from __future__ import annotations

import json
from importlib import metadata as _metadata

import typer

from .algorithms import binary_search, fibonacci, fibonacci_fast, gcd
from .config import load_config
from .connectors import Connector, FileSystemConnector, SQLiteConnector
from .excel_tools import write_rows_to_excel
from .logging_utils import configure_logging_from_cli
from .ml_pipeline import (
    add_bias_feature,
    load_model,
    predict,
    save_model,
    train_linear_regression,
)
from .monitor import ping_url, send_slack_webhook
from .vin import compute_check_digit, decode_vin, generate_vin, is_valid_vin

app = typer.Typer(help="Python Mastery Portfolio CLI")


@app.callback(invoke_without_command=True)
def _global_options(ctx: typer.Context, verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"), config: str | None = typer.Option(None, "--config", "-c", help="Path to TOML config file"), json_logs: bool = typer.Option(False, "--json-logs", help="Emit logs in JSON format"),) -> None:
    configure_logging_from_cli(verbose=verbose, json_output=json_logs)
    if config:
        try:
            ctx.obj = {"config": load_config(config)}
        except Exception:
            raise typer.Exit(code=2)


@app.command()
def fib(
    n: int = typer.Argument(..., min=0, help="Return the n-th Fibonacci number (0-indexed)"),
) -> None:
    """Compute the n-th Fibonacci number."""
    typer.echo(fibonacci(n))


@app.command("gcd")
def gcd_cmd(
    a: int = typer.Argument(..., help="First integer"),
    b: int = typer.Argument(..., help="Second integer"),
) -> None:
    """Compute the greatest common divisor of two integers."""
    try:
        res = gcd(a, b)
    except ValueError as e:
        raise typer.Exit(code=2) from e
    typer.echo(str(res))


@app.command("benchmark")
def benchmark_cmd(n: int = typer.Option(20, "--n", "-n"), iterations: int = typer.Option(1000, "--iterations", "-i"), warmup: int = typer.Option(3, "--warmup", "-w"), method: str = typer.Option("both", "--method"), json_out: bool = typer.Option(False, "--json"),) -> None:
    import time
    from statistics import mean

    def time_func(func):
        for _ in range(warmup):
            func(n)
        timings = []
        for _ in range(iterations):
            s = time.perf_counter()
            func(n)
            timings.append((time.perf_counter() - s) * 1000)
        return {"iterations": iterations, "total_ms": sum(timings), "avg_ms": mean(timings)}

    out = {}
    if method in ("iterative", "both"):
        out["iterative"] = time_func(fibonacci)
    if method in ("fast", "both"):
        out["fast"] = time_func(fibonacci_fast)
    if json_out:
        typer.echo(json.dumps(out, sort_keys=True))
        return
    for k, v in out.items():
        typer.echo(f"{k}: iterations={v['iterations']} total_ms={v['total_ms']:.3f}")
        typer.echo(f"{k}: avg_ms={v['avg_ms']:.6f}")


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


def run() -> None:  # pragma: no cover
    app()


@app.command("version")
def version_cmd() -> None:
    """Print the package version."""
    try:
        ver = _metadata.version("python-mastery-portfolio")
    except Exception:
        ver = "0.0.0"
    typer.echo(ver)


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


@app.command("vin-decode")
def vin_decode_cmd(vin: str = typer.Argument(..., help="17-character VIN")) -> None:
    """Decode a VIN (WMI/VDS/VIS, year, plant, region, brand)."""
    dec = decode_vin(vin)
    # Print as lightweight key=value lines for readability
    fields = [
        ("vin", dec.vin),
        ("valid", str(dec.valid)),
        ("wmi", dec.wmi),
        ("vds", dec.vds),
        ("vis", dec.vis),
        ("check_digit", dec.check_digit),
        ("model_year_code", dec.model_year_code or ""),
        ("model_year", str(dec.model_year) if dec.model_year is not None else ""),
        ("plant_code", dec.plant_code or ""),
        ("serial_number", dec.serial_number or ""),
        ("region", dec.region or ""),
        ("brand", dec.brand or ""),
    ]
    for k, v in fields:
        typer.echo(f"{k}={v}")


@app.command("vin-generate")
def vin_generate_cmd(
    wmi: str = typer.Option(..., "--wmi", help="World Manufacturer Identifier (3 chars)"),
    vds: str = typer.Option(..., "--vds", help="Vehicle Descriptor Section (5 chars)"),
    year: int = typer.Option(..., "--year", min=1980, max=2039, help="Model year"),
    plant: str = typer.Option(..., "--plant", help="Plant code (1 char)"),
    serial: str = typer.Option(..., "--serial", help="Serial (6 chars)"),
) -> None:
    """Generate a valid VIN from components (computes check digit)."""
    try:
        vin = generate_vin(wmi, vds, year, plant, serial)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e
    typer.echo(vin)


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
    url: str = typer.Argument(..., help="URL to ping, e.g. http://localhost:8000/health"),
    iterations: int = typer.Option(1, "--iterations", "-n", min=1, help="Number of pings"),
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


@app.command("ingest")
def ingest(
    source: str = typer.Argument(..., help="Source path or DB connection string"),
    kind: str = typer.Option("fs", "--kind", help="Connector kind: fs|sqlite"),
    output: str = typer.Option("out.jsonl", "--output", help="Output JSONL path"),
    table: str | None = typer.Option(None, "--table", help="Table name (for sqlite)"),
) -> None:
    """Run a connector to produce JSONL output. Supported kinds: fs, sqlite.

    Examples:
      pm-portfolio ingest ./docs --kind fs --output docs.jsonl
      pm-portfolio ingest data.db --kind sqlite --table documents --output data.jsonl
    """
    conn: Connector
    if kind == "fs":
        conn = FileSystemConnector(source)
    elif kind == "sqlite":
        if not table:
            raise typer.BadParameter("--table is required for sqlite connectors")
        conn = SQLiteConnector(source, table)
    else:
        raise typer.BadParameter("unknown connector kind")
    path = conn.to_jsonl(output)
    typer.echo(str(path))


@app.command("qa-eval")
def qa_eval_cmd(
    docs_jsonl: str = typer.Argument(
        ..., help="Documents JSONL (from pm-portfolio ingest)", metavar="DOCS.jsonl"
    ),
    eval_jsonl: str = typer.Argument(..., help="Evaluation dataset JSONL", metavar="EVAL.jsonl"),
    k: int = typer.Option(5, "--k", min=1, help="Top-k retrieval depth"),
    chunk_size: int = typer.Option(800, "--chunk-size", min=100, help="Chunk size in characters"),
    chunk_overlap: int = typer.Option(
        100, "--chunk-overlap", min=0, help="Chunk overlap in characters"
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON"),
) -> None:
    """Evaluate offline retrieval quality (recall@k and MRR).

    Dataset JSONL format (one object per line):
        {"question": "...", "gold_contains": "some phrase"}
    or:
        {"question": "...", "gold_doc_id": "<id from docs.jsonl>"}
    """
    from .qa_eval import evaluate_from_jsonl

    res = evaluate_from_jsonl(
        docs_jsonl=docs_jsonl,
        eval_jsonl=eval_jsonl,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        k=k,
    )
    if as_json:
        typer.echo(json.dumps(res, indent=2, ensure_ascii=False))
        return
    from typing import cast

    typer.echo(f"n={res.get('n')} k={res.get('k')}")
    recall_val = cast(float, res.get("recall_at_k", 0.0))
    mrr_val = cast(float, res.get("mrr", 0.0))
    typer.echo(f"recall@k={float(recall_val):.3f}")
    typer.echo(f"mrr={float(mrr_val):.3f}")
