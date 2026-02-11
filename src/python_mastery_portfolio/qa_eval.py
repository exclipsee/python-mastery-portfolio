from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .doc_qa import QADocument, QAService


@dataclass(frozen=True)
class EvalExample:
    question: str
    gold_contains: str | None = None
    gold_doc_id: str | None = None


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    p = Path(path)
    rows: list[dict[str, Any]] = []
    with p.open("r", encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if not isinstance(obj, dict):
                raise ValueError("jsonl line is not an object")
            rows.append(obj)
    return rows


def load_documents_jsonl(path: str | Path) -> list[QADocument]:
    rows = load_jsonl(path)
    docs: list[QADocument] = []
    for r in rows:
        doc_id = str(r.get("id", ""))
        text = str(r.get("text", ""))
        meta_raw = r.get("metadata", {})
        if not isinstance(meta_raw, dict):
            meta_raw = {}
        if not doc_id or not text:
            continue
        docs.append(QADocument(id=doc_id, text=text, metadata={str(k): v for k, v in meta_raw.items()}))
    return docs


def load_eval_examples_jsonl(path: str | Path) -> list[EvalExample]:
    rows = load_jsonl(path)
    out: list[EvalExample] = []
    for r in rows:
        q = r.get("question")
        if not isinstance(q, str) or not q.strip():
            continue
        gc = r.get("gold_contains")
        gid = r.get("gold_doc_id")
        out.append(EvalExample(question=q, gold_contains=str(gc) if isinstance(gc, str) else None, gold_doc_id=str(gid) if isinstance(gid, str) else None))
    return out


def _match_hit(
    *,
    hit_text: str,
    hit_doc_id: str | None,
    example: EvalExample,
) -> bool:
    if example.gold_doc_id is not None:
        return hit_doc_id == example.gold_doc_id
    if example.gold_contains is not None:
        return example.gold_contains.lower() in hit_text.lower()
    return False


def evaluate_retrieval(
    *,
    qa: QAService,
    examples: list[EvalExample],
    k: int = 5,
) -> dict[str, object]:
    """Evaluate retrieval quality using recall@k and MRR.

    Each example should specify either `gold_contains` or `gold_doc_id`.
    """
    if k <= 0:
        raise ValueError("k must be positive")

    n = 0
    hits_found = 0
    mrr_sum = 0.0
    details: list[dict[str, object]] = []

    for ex in examples:
        if ex.gold_contains is None and ex.gold_doc_id is None:
            continue
        n += 1
        hits = qa.search_rich(ex.question, k=k)
        found_rank: int | None = None
        for idx, h in enumerate(hits):
            meta = h.meta or {}
            doc_id = meta.get("doc_id")
            doc_id_s = str(doc_id) if isinstance(doc_id, str) else None
            if _match_hit(hit_text=h.text, hit_doc_id=doc_id_s, example=ex):
                found_rank = idx
                break

        if found_rank is not None:
            hits_found += 1
            mrr_sum += 1.0 / float(found_rank + 1)

        details.append(
            {
                "question": ex.question,
                "found": found_rank is not None,
                "rank": found_rank,
                "top_hit": hits[0].text if hits else "",
            }
        )

    recall_at_k = (hits_found / n) if n else 0.0
    mrr = (mrr_sum / n) if n else 0.0
    return {
        "n": n,
        "k": k,
        "recall_at_k": recall_at_k,
        "mrr": mrr,
        "details": details,
    }


def evaluate_from_jsonl(
    *,
    docs_jsonl: str | Path,
    eval_jsonl: str | Path,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
    k: int = 5,
) -> dict[str, object]:
    docs = load_documents_jsonl(docs_jsonl)
    examples = load_eval_examples_jsonl(eval_jsonl)
    qa = QAService()
    qa.add_documents(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return evaluate_retrieval(qa=qa, examples=examples, k=k)
