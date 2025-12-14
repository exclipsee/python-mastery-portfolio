# Overview

Python Mastery Portfolio is a compact, well-tested collection of practical
Python examples and small services. It demonstrates clean, typed code, a
developer-friendly CLI, a Streamlit demo, lightweight FastAPI endpoints, and
connector primitives for ingestion workflows (filesystem / SQLite → JSONL).

This repository is intended as a short, interview-ready showcase you can run
locally in minutes.

---

## Table of contents

- [Highlights](#highlights)
- [Quick start](#quick-start)
- [Try the demo](#try-the-demo)
- [Examples (CLI & API)](#examples-cli--api)
# Overview

Python Mastery Portfolio is a compact, well-tested collection of practical
Python examples and small services. It demonstrates clean, typed code, a
developer-friendly CLI, a Streamlit demo, lightweight FastAPI endpoints, and
connector primitives for ingestion workflows (filesystem / SQLite → JSONL).

This repository is intended as a short, interview-ready showcase you can run
locally in minutes.

---

## Table of contents

- [Highlights](#highlights)
- [Quick start](#quick-start)
- [Try the demo](#try-the-demo)
- [Examples (CLI & API)](#examples-cli--api)
- [Development](#development)
- [Project structure](#project-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Contact & License](#contact--license)

---

## Highlights

- Small CLI (`pm-portfolio`) with practical commands (Fibonacci, VIN tools,
  monitoring, ingestion helpers).
- Streamlit demo for fast hands-on evaluation without deep setup.
- Connector primitives that export JSONL for downstream embedding/indexing
  workflows (Filesystem, SQLite).
- Minimal FastAPI examples and WebSocket-based monitoring helpers for demos.

---

## Quick start

Prerequisites: Python 3.10+ and Git.

Clone, create a venv, install dev deps, and run the test suite:

```powershell
git clone https://github.com/exclipsee/python-mastery-portfolio.git
cd python-mastery-portfolio
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .[dev]
pytest -q
```

If you prefer pip-only without extras:

```powershell
pip install -r requirements.txt
```

---

## Try the demo

Run the Streamlit demo (optional extras):

```powershell
pip install -e .[demo]
streamlit run demo/streamlit_app.py
```

Open the app in your browser and explore the CLI-backed features and
local fallbacks.

---

## Examples (CLI & API)

- Ingest a folder to `docs.jsonl`:

```powershell
pm-portfolio ingest ./docs --kind fs --output docs.jsonl
```

- Ingest a SQLite table to JSONL:

```powershell
pm-portfolio ingest data.db --kind sqlite --table documents --output data.jsonl
```

- Run the API locally (FastAPI):

```powershell
uvicorn python_mastery_portfolio.api:app --reload
```

- WebSocket monitoring (broadcasts system metrics every 2s):

``
ws://localhost:8000/ws/metrics
``

---

## Development

- Lint and auto-fix selected files with ruff:

```powershell
python -m ruff check --fix src tests
```

- Type checks:

```powershell
mypy src
```

- Run a single test file:

```powershell
pytest -q tests/test_connectors.py
```

---

## Project structure

```
.
├─ demo/                      # Streamlit demo app
├─ src/python_mastery_portfolio/  # package modules (api, cli, connectors, utils)
├─ tests/                     # unit tests
├─ benchmarks/                # optional micro-benchmarks
├─ cdk/                       # optional AWS CDK examples
```

---

## Architecture (quick view)

```mermaid
flowchart LR
	Files[Files / Docs] -->|ingest| Connectors[Connectors (fs/sqlite)]
	Connectors -->|jsonl| Embedding[Embeddings / Indexing]
	Embedding -->|search| API[Retrieval API / FastAPI]
	DemoStream[Streamlit Demo] --> API
```

Note: `Embedding` and `Indexing` are roadmap items — connectors produce
portable JSONL for consumption by an embedding pipeline.

---

## Roadmap

- Add embedding wrappers (simple deterministic + sentence-transformers).
- Provide local FAISS indexer and Postgres `pgvector` adapter.
- Add retrieval service (ingest → index → query) and demo notebooks.

---

## Contributing

Contributions are welcome. Please keep commits small, include tests for
behavioral changes, and follow the formatting rules in `pyproject.toml`.

Suggested workflow:

1. Fork & branch
2. Run tests and linters locally
3. Open a PR with a clear description and a few usage examples

---

## Contact & License

- Author: Volodymyr Minutin — `volodymyr.minutin@gmail.com`
- License: MIT

---

If you approve this README I can commit and push it — reply `commit and push`.
