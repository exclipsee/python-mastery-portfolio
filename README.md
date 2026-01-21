# python-mastery-portfolio

[![CI](https://github.com/exclipsee/python-mastery-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/exclipsee/python-mastery-portfolio/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A personal collection of compact, well-tested Python utilities and examples
designed to demonstrate practical engineering skills: typed code, clear
APIs, benchmarks, and small ML / RAG examples.

**Highlights**

- Purpose-built for portfolio use: readable implementations, thorough tests,
	simple benchmarks, and a small FastAPI service to demonstrate HTTP design.
- Clean, modern typing and docstrings across modules.
- Examples: Fibonacci algorithms (iterative + fast-doubling), VIN utilities,
	a tiny ML training/predict flow, and a document Q&A demo.

**Tech stack & tools**

- Python 3.11+ with type hints
- FastAPI for the HTTP demo
- pytest for tests, simple benchmark scripts in `benchmarks/`

**Quickstart**

Install the project in editable mode and run tests:

```bash
python -m venv .venv
source .venv/Scripts/activate   # on Windows: .venv\Scripts\Activate.ps1
pip install -e .
pytest -q
```

Run the example API locally:

```bash
uvicorn python_mastery_portfolio.api:app --reload --host 127.0.0.1 --port 8000
```

Run the Fibonacci benchmark (example):

```bash
python benchmarks/benchmark_fib.py --iterations 1000 --n 30 --warmup 5
```

Example API usage (ask for a Fibonacci value):

```bash
curl "http://127.0.0.1:8000/fib/20"
# => {"n":20,"value":6765}
```

**Project layout (important files)**

- `src/python_mastery_portfolio/` — main library, API, CLI, and utilities
- `tests/` — unit and integration tests (pytest)
- `benchmarks/` — simple microbenchmarks and scripts

**What I can expand to showcase more skills**

- Add a professional CLI with subcommands and tab-completion
- Add CI (GitHub Actions) and coverage/linting badges
- Include a `Dockerfile` + `docker-compose` demo for deployment
- Add notebooks or short tutorials demonstrating RAG/embeddings

If you want, I can: add a polished README case study section describing a
short problem I solved inside this repo (motivation, approach, results),
or implement CI and badges so the repo looks ready for hiring review.

---

License: MIT — Volodymyr Minutin <volodymyr.minutin@gmail.com>

**Docker / Quick demo**

You can run the FastAPI demo in a container for an environment-independent demo.

Build and run with Docker:

```bash
docker build -t pm-portfolio .
docker run --rm -p 8000:8000 pm-portfolio
```

Or use docker-compose for local development with live reload:

```bash
docker-compose up --build
```

Then visit http://127.0.0.1:8000/docs for the API docs.

**Streamlit live demo**

There is a small interactive demo that queries the API and visualises semantic
search results using embeddings. Install demo extras and run:

```bash
pip install -e .[demo]
streamlit run examples/streamlit_demo.py
```



