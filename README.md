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

# ask and inspect retrieved chunks + metadata
Invoke-RestMethod "http://localhost:8000/qa/ask_rich?question=What%20is%20FastAPI%3F&k=5" -Method Post
```

Notes

- CLI: global `--json-logs` and `--config` (TOML/JSON) supported.
- `pm-portfolio version` prints package version.

License: MIT — Volodymyr Minutin <volodymyr.minutin@gmail.com>

