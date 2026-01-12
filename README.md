# python-mastery-portfolio

A compact collection of Python projects and utilities showcasing clean,
typed, and well-tested code. This repository is curated as a personal
portfolio to demonstrate practical Python skills.

Quick start

- Run tests:

  `pytest -q`

- Run the small API (development):

  `uvicorn python_mastery_portfolio.api:app --reload --host 127.0.0.1 --port 8000`

- Run a CLI example (after installing the package):

  `pm-portfolio fib 10`

What you'll find

- `src/python_mastery_portfolio/`: library modules, CLI, and API.
- `tests/`: unit and integration tests that demonstrate design and quality.
- `benchmarks/`: optional performance experiments.

Contributing / Notes

- The repository is intentionally minimal—it highlights code quality and
  practical examples rather than infra or CI artifacts.
- If you want a small runnable demo or single-page showcase, I can add
  a focused example with clear instructions.

License

MIT — Volodymyr Minutin <volodymyr.minutin@gmail.com>
# Overview

 # python-mastery-portfolio

Compact examples and small utilities demonstrating clean, typed, and
well-tested Python code.

Common commands

- `pm-portfolio fib 10` — compute Fibonacci
- `pm-portfolio ingest ./docs --kind fs --output docs.jsonl` — produce JSONL
- `pm-portfolio qa-eval docs.jsonl eval.jsonl` — evaluate offline retrieval (recall@k, MRR)
- `uvicorn python_mastery_portfolio.api:app --reload` — run API

Offline RAG / Document Q&A (API)

```powershell
uvicorn python_mastery_portfolio.api:app --reload

# ingest structured docs (chunked) into the in-memory QA index
Invoke-RestMethod http://localhost:8000/qa/ingest -Method Post -ContentType application/json -Body (
	@{ reset=$true; chunk_size=400; chunk_overlap=50; documents=@(
			@{ id='doc1'; text='FastAPI is a Python web framework.'; metadata=@{source='demo'} },
			@{ id='doc2'; text='Pandas supports data analysis.'; metadata=@{source='demo'} }
		)
	} | ConvertTo-Json -Depth 5
)

Invoke-RestMethod "http://localhost:8000/qa/ask_rich?question=What%20is%20FastAPI%3F&k=5" -Method Post
```

Notes

- CLI: global `--json-logs` and `--config` (TOML/JSON) supported.
- `pm-portfolio version` prints package version.

License: MIT — Volodymyr Minutin <volodymyr.minutin@gmail.com>

