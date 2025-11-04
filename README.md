# Python Mastery Portfolio

I built this repository to showcase how I write Python: clean, typed, tested, and production‑ready. It includes a small CLI, idiomatic modules, and full developer tooling so you can quickly evaluate how I work.

[![CI](https://github.com/exclipsee/python-mastery-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/exclipsee/python-mastery-portfolio/actions)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![ruff](https://img.shields.io/badge/lint-ruff-%23cc0000)
![mypy](https://img.shields.io/badge/types-mypy-2A6DB2)

## What this repo demonstrates

- Clean, well-documented modules (algorithms, utilities)
- A small, user-friendly CLI (`pm-portfolio`) built with Typer
- Strong typing (mypy), formatting (black), linting (ruff), and tests (pytest + coverage)
- Continuous Integration with GitHub Actions

## Highlights

- Python >= 3.10
- Modern project layout (`src/`)
- 100% type-hinted public APIs with docstrings
- Tests cover examples and behavior, with full coverage across modules

## Quick start

Create a virtual environment and install in editable mode with developer tools:

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
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
	- `POST /qa/reset` — clear store
	- `POST /qa/documents` — body: JSON array of strings; returns ids
	- `POST /qa/search?query=...&k=5` — returns top-k hits
	- `POST /qa/ask?question=...&k=3` — returns naive answer + hits
- Optional extras: `pip install -e .[rag]` to experiment with sentence-transformers/FAISS.

### CI Matrix

- GitHub Actions runs on Python 3.10, 3.11, 3.12, 3.13

### Optional: Publish to TestPyPI

- Workflow `.github/workflows/publish-testpypi.yml` publishes on tag like `v0.1.0`
- Add a secret `TEST_PYPI_API_TOKEN` in GitHub repo settings to enable

### Containers & Cloud

- Dockerfile included to run the API with Uvicorn:

```powershell
docker build -t python-mastery-portfolio .
docker run -p 8000:8000 python-mastery-portfolio
```

- Coverage is uploaded via GitHub Actions to Codecov (configure in repo settings).

### AWS CDK (optional)

I include an AWS CDK example (in `cdk/`) to deploy the Dockerized API to ECS Fargate with an ALB in `eu-central-1` (Frankfurt). This requires an AWS account and one-time CDK bootstrap in your account/region. See `cdk/README.md` for steps.

Run the API locally (optional):

```powershell
uvicorn python_mastery_portfolio.api:app --reload
```

### Frontend demo (optional)

- Install demo extras and run the Streamlit app:

```powershell
pip install -e .[demo]
streamlit run demo/streamlit_app.py
```

Configuration:

- The app resolves the API base URL in this order: environment variable `API_URL` > Streamlit `secrets.toml` > default `http://localhost:8000`.
- To configure secrets, create either `%USERPROFILE%/.streamlit/secrets.toml` or `demo/.streamlit/secrets.toml`:

```
API_URL = "http://localhost:8000"
```

Alternatively, set an environment variable before launching Streamlit:

```powershell
$env:API_URL = "http://localhost:8000"
streamlit run demo/streamlit_app.py
```

Demo includes VIN decode UI calling `/vin/decode` to show WMI/region/year/plant details.

## About me

- I’m Volodymyr Minutin — a Computer Science student and Python developer with ~4 years of experience.
- I love building automotive‑related tools in Python (I’m a car enthusiast).
- Tools I’m comfortable with include Python, CLI design (Typer), testing (pytest), type checking (mypy), and automation/CI.
- I also have practical skills with MS Office (especially Excel) and can automate workflows end‑to‑end.
- Languages: Russian (native), Ukrainian (native), Polish (C2), English (C1), German (B1).

## How I work

- Favor clear APIs, small modules, and strong typing for maintainability.
- Treat tooling as part of the product: formatting, linting, typing, and tests run locally and in CI.
- Keep examples practical and focused; include a CLI for fast manual testing.

## CI status

CI runs on GitHub Actions (see `.github/workflows/ci.yml`). The badge above reflects the latest status on GitHub once the repo is pushed.

## Contact

- Email: volodymyr.minutin@gmail.com
- LinkedIn: https://www.linkedin.com/in/volodymyr-minutin-380310364
- GitHub: https://github.com/exclipsee

## License

MIT