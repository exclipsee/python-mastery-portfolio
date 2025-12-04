# python-mastery-portfolio

[![CI](https://github.com/exclipsee/python-mastery-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/exclipsee/python-mastery-portfolio/actions)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)

Small, well-tested Python utilities and demos focused on data, ML, and practical engineering.

Core highlights
- Polished demo app under `demo/streamlit_app.py` — Streamlit UI with an offline fallback so reviewers can try features without running the API. Features include:
  - Fibonacci calculator (API or local fallback)
  - VIN validation & decode (uses local `vin.py` helpers if API is unavailable)
  - Lightweight CSV export/download fallback for quick demos
  - Placeholder for real-time WebSocket monitoring (coming soon)
- CLI and utilities in `src/python_mastery_portfolio/` (VIN helpers, ML utilities, monitoring helpers).
- Tests under `tests/` with focused unit coverage for core utilities.

What's new
- The Streamlit demo has been polished: added a sidebar with demo controls, sample VIN/CSV presets, and local fallbacks so the demo works offline and is recruiter-friendly. The app now emphasizes quick, explorable outputs and full JSON expanders for transparency.

Quick repo map
- `demo/` — interactive demo app and demo assets
- `src/python_mastery_portfolio/` — package modules and CLI
- `tests/` — pytest tests
- `benchmarks/` — small benchmarking examples

Next ideas (planned)
- Add a deployable FastAPI example with OpenAPI and Docker
- Add CI workflows to auto-deploy the demo and enforce linting/typing
- Expand benchmarking and add explainability reports for ML pipelines

About me
- Volodymyr Minutin — Computer Science student and Python developer. Focus: clean code, strong typing, practical demos, and automation.

Contact
---
# Python Mastery Portfolio 🚗⚙️

[![CI](https://github.com/exclipsee/python-mastery-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/exclipsee/python-mastery-portfolio/actions) ![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)

A compact collection of practical Python utilities, a small CLI, a demo
Streamlit app, and example ingestion/connectors for experimenting with
embeddings/indexing and lightweight ML pipelines.

Why this repo?
- Fast to run locally — designed for quick demos during interviews or tech
	walkthroughs.
- Focus on clean, typed code, tests, and reproducible developer tooling.

Highlights ✨
- CLI: `pm-portfolio` — Fibonacci, VIN tools, monitoring, and ingest helpers.
- Demo: `demo/streamlit_app.py` for quick interactive exploration.
- Connectors: Filesystem + SQLite → JSONL (ready for embedding/indexing).
- Monitoring: WebSocket metrics + Prometheus-style endpoints for demos.

Quickstart (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .[dev]
pytest -q
```

Try the demo
```powershell
pip install -e .[demo]
streamlit run demo/streamlit_app.py
```

Small examples
- Ingest a folder:
```powershell
pm-portfolio ingest ./docs --kind fs --output docs.jsonl
```
- Ingest a SQLite table:
```powershell
pm-portfolio ingest data.db --kind sqlite --table documents --output data.jsonl
```

Developer notes
- Run lint + types:
```powershell
ruff check src tests
mypy src
```
- Fix a file with ruff:
```powershell
python -m ruff check --fix src/python_mastery_portfolio/connectors.py
```

Repo layout
- `src/python_mastery_portfolio/` — code + CLI
- `demo/` — Streamlit app
- `tests/` — pytest
- `benchmarks/`, `cdk/` — optional extras

Roadmap (short)
- Add embeddings + FAISS/pgvector indexer
- Retrieval API (ingest → index → query) and demo notebook

Contact
- Email: `volodymyr.minutin@gmail.com`
- GitHub: `https://github.com/exclipsee`

License: MIT

---

Want this pushed? Reply `commit and push` and I'll commit & push the README update for you.
pip install -U pip
pip install -e .[dev]
```

Run the full quality suite:

```powershell
pytest
ruff check .
black --check .
mypy
```

Try the CLI:

```powershell
pm-portfolio --help
pm-portfolio fib 10
pm-portfolio search --value 42 1 2 3 40 41 42 100
```

## Repo structure

- `src/python_mastery_portfolio/` – package modules and CLI
- `tests/` – pytest tests
- `.github/workflows/ci.yml` – CI pipeline
- `pyproject.toml` – config for tooling and packaging
  
### Bonus examples included

- `vin.py` — VIN validation (ISO 3779) with CLI commands:
	- `pm-portfolio vin-validate <VIN>`
	- `pm-portfolio vin-check <VIN>`
		- `pm-portfolio vin-decode <VIN>`
		- `pm-portfolio vin-generate --wmi 1HG --vds CM826 --year 2003 --plant A --serial 004352`
- `api.py` — a tiny FastAPI app exposing `/fib/{n}` and Pydantic-based `/vin/validate`
	and extended VIN endpoints: `/vin/decode` and `/vin/generate`
- `ml_pipeline.py` — simple scikit-learn pipeline (StandardScaler + LinearRegression) with optional bias feature engineering and model persistence (joblib) wired into the CLI

### API Observability

- Adds `X-Process-Time` and `X-Request-ID` headers to every response
- JSON logging with request metadata; request-id is propagated if provided

### Monitoring (optional)

- CLI: `pm-portfolio monitor-ping http://localhost:8000/health -n 5 -i 0.2`
- API endpoints: `/monitor/ping?url=...`, `/metrics` (Prometheus format), `/monitor/connections`
- **Real-time WebSocket monitoring**: `ws://localhost:8000/ws/metrics` broadcasts system metrics every 2 seconds
- Extras: `pip install -e .[monitoring]` to enable Prometheus metrics collection and system monitoring

### Document Q&A (MVP)

- Add documents, semantic search, and ask a question over your text using a deterministic embedder for demos/tests.
- Endpoints:
	---
	# Python Mastery Portfolio

	[![CI](https://github.com/exclipsee/python-mastery-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/exclipsee/python-mastery-portfolio/actions)
	![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)

	Practical, well-tested Python utilities and demos showcasing clean code, typing,
	and developer tooling. The project includes a small CLI, a demo Streamlit app,
	example FastAPI endpoints, and connector primitives for ingestion workflows.

	**Quick Links**
	- **Source:** `src/python_mastery_portfolio/`
	- **Demo app:** `demo/streamlit_app.py`
	- **Tests:** `tests/`
	- **CLI entry:** `src/python_mastery_portfolio/cli.py`

	## Features
	- CLI utilities: Fibonacci, VIN helpers, monitoring and a small ML demo pipeline.
	- Demo: a Streamlit UI for interactively exercising features and local fallbacks.
	- Connectors: filesystem and SQLite connectors that output JSONL for downstream
		embedding/indexing workflows.
	- Monitoring: optional WebSocket-based system metrics and Prometheus-style
		endpoints for demo purposes.

	## Quickstart (Windows PowerShell)
	Create and activate a virtual environment, install development extras, and run
	tests:

	```powershell
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	pip install -U pip
	pip install -e .[dev]
	pytest -q
	```

	Run the Streamlit demo (optional):

	```powershell
	pip install -e .[demo]
	streamlit run demo/streamlit_app.py
	```

	Run the API locally:

	```powershell
	uvicorn python_mastery_portfolio.api:app --reload
	```

	## Examples

	- Ingest a directory using the CLI connector (produces `out.jsonl`):

	```powershell
	pm-portfolio ingest ./docs --kind fs --output docs.jsonl
	```

	- Ingest a SQLite table:

	```powershell
	pm-portfolio ingest data.db --kind sqlite --table documents --output data.jsonl
	```

	- WebSocket monitoring (broadcasts system metrics every 2s):

	```
	ws://localhost:8000/ws/metrics
	```

	## Development
	- Run the full quality suite:

	```powershell
	pytest
	ruff check src tests
	mypy src
	```

	- Lint/fix a file with ruff:

	```powershell
	python -m ruff check --fix src/python_mastery_portfolio/connectors.py
	```

	## Structure
	- `src/python_mastery_portfolio/` — package modules (connectors, API, CLI)
	- `demo/` — Streamlit demo
	- `tests/` — unit tests (pytest)
	- `benchmarks/` — small benchmarking scripts
	- `cdk/` — optional AWS CDK deployment example

	## Next steps (roadmap)
	- Add embedding and indexing primitives (FAISS / pgvector adapters).
	- Build a small retrieval API (ingest → index → query) and demo notebook.
	- Add additional connectors (HTTP/Confluence, Postgres) and e2e tests.

	## Contributing
	PRs welcome — keep changes focused and include tests. See `pyproject.toml`
	for formatting and typing rules (ruff, black, mypy).

	## Contact
	- Email: `volodymyr.minutin@gmail.com`
	- GitHub: `https://github.com/exclipsee`

	## License
	MIT

	---

	If you'd like, I can also commit and push this change for you. Say "commit and push" and I'll run the git commands.