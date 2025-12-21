# Overview

 # python-mastery-portfolio

Compact examples and small utilities demonstrating clean, typed, and
well-tested Python code.

Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .[dev]
pytest -q
```

Run the demo (optional):

```powershell
pip install -e .[demo]
streamlit run demo/streamlit_app.py
```

Common commands

- `pm-portfolio fib 10` — compute Fibonacci
- `pm-portfolio ingest ./docs --kind fs --output docs.jsonl` — produce JSONL
- `uvicorn python_mastery_portfolio.api:app --reload` — run API

Notes

- CLI: global `--json-logs` and `--config` (TOML/JSON) supported.
- `pm-portfolio version` prints package version.

License: MIT — Volodymyr Minutin <volodymyr.minutin@gmail.com>

