---
# Python Mastery Portfolio

[![CI](https://github.com/exclipsee/python-mastery-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/exclipsee/python-mastery-portfolio/actions) ![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)

A compact, professional codebase demonstrating clean Python practices:
typed APIs, unit tests, CLI ergonomics, and small services for data/ML tasks.

**Key Capabilities**
- CLI (`pm-portfolio`): Fibonacci, VIN utilities, monitoring, and ingestion.
- Demo: Streamlit app for hands-on evaluation without additional setup.
- Connectors: Filesystem and SQLite → JSONL for downstream pipelines.
- Services: Minimal FastAPI endpoints and optional WebSocket monitoring.

**Quick Start (Windows PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .[dev]
pytest -q
```

Run the demo app:
```powershell
pip install -e .[demo]
streamlit run demo/streamlit_app.py
```

**Examples**
- Ingest a folder:
```powershell
pm-portfolio ingest ./docs --kind fs --output docs.jsonl
```
- Ingest a SQLite table:
```powershell
pm-portfolio ingest data.db --kind sqlite --table documents --output data.jsonl
```

**Development**
```powershell
ruff check src tests
mypy src
```

**Structure**
- `src/python_mastery_portfolio/` — modules and CLI
- `demo/` — Streamlit demo
- `tests/` — unit tests

**Contributing**
- Keep changes focused; include tests. See `pyproject.toml` for tooling.

**Contact**
- Email: volodymyr.minutin@gmail.com

**License**
- MIT

---
