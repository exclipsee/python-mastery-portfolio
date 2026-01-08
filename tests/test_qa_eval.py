from __future__ import annotations

from pathlib import Path

from python_mastery_portfolio.qa_eval import evaluate_from_jsonl


def test_evaluate_from_jsonl(tmp_path: Path) -> None:
    docs = tmp_path / "docs.jsonl"
    docs.write_text(
        """
{"id":"d1","text":"FastAPI is a Python web framework.","metadata":{"path":"a"}}
{"id":"d2","text":"Pandas supports data analysis.","metadata":{"path":"b"}}
""".strip()
        + "\n",
        encoding="utf8",
    )

    dataset = tmp_path / "eval.jsonl"
    dataset.write_text(
        """
{"question":"What is FastAPI?","gold_contains":"FastAPI"}
{"question":"What library is for data analysis?","gold_contains":"Pandas"}
""".strip()
        + "\n",
        encoding="utf8",
    )

    res = evaluate_from_jsonl(docs_jsonl=docs, eval_jsonl=dataset, k=2, chunk_size=80, chunk_overlap=10)
    assert res["n"] == 2
    assert 0.0 <= float(res["recall_at_k"]) <= 1.0
    assert 0.0 <= float(res["mrr"]) <= 1.0
    assert isinstance(res["details"], list)
