from __future__ import annotations

import math
import re
from collections.abc import Iterable
from dataclasses import dataclass


def _tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[A-Za-z0-9']+", text.lower()) if t]


class SimpleEmbedder:
    """A deterministic bag-of-words embedder for tests and demo.

    Maps tokens to counts and projects into a fixed dictionary order vector.
    """

    def __init__(self) -> None:
        self.vocab: dict[str, int] = {}

    def fit(self, docs: Iterable[str]) -> None:
        for d in docs:
            for tok in _tokenize(d):
                if tok not in self.vocab:
                    self.vocab[tok] = len(self.vocab)

    def _vec(self, text: str) -> list[float]:
        v = [0.0] * len(self.vocab)
        for tok in _tokenize(text):
            idx = self.vocab.get(tok)
            if idx is not None:
                v[idx] += 1.0
        return v

    def embed(self, texts: Iterable[str]) -> list[list[float]]:
        return [self._vec(t) for t in texts]


def _cosine(a: list[float], b: list[float]) -> float:
    num = sum(x * y for x, y in zip(a, b, strict=True))
    da = math.sqrt(sum(x * x for x in a))
    db = math.sqrt(sum(y * y for y in b))
    if da == 0.0 or db == 0.0:
        return 0.0
    return num / (da * db)


@dataclass
class Document:
    id: int
    content: str
    embedding: list[float]


class DocumentStore:
    def __init__(self, embedder: SimpleEmbedder | None = None) -> None:
        self.embedder = embedder or SimpleEmbedder()
        self._docs: list[Document] = []
        self._next_id = 1

    def add_documents(self, docs: Iterable[str]) -> list[int]:
        ds = list(docs)
        # grow vocab first
        self.embedder.fit(ds)
        embs = self.embedder.embed(ds)
        ids: list[int] = []
        for content, emb in zip(ds, embs, strict=True):
            doc = Document(id=self._next_id, content=content, embedding=emb)
            self._docs.append(doc)
            ids.append(doc.id)
            self._next_id += 1
        return ids

    def reset(self) -> None:
        self.embedder = SimpleEmbedder()
        self._docs.clear()
        self._next_id = 1

    def search(self, query: str, k: int = 5) -> list[tuple[int, float, str]]:
        q_emb = self.embedder.embed([query])[0]
        scored = [
            (d.id, _cosine(q_emb, d.embedding), d.content) for d in self._docs
        ]
        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[: max(0, k)]


class QAService:
    def __init__(self, store: DocumentStore | None = None) -> None:
        self.store = store or DocumentStore()

    def add(self, docs: Iterable[str]) -> list[int]:
        return self.store.add_documents(docs)

    def reset(self) -> None:
        self.store.reset()

    def search(self, query: str, k: int = 5) -> list[tuple[int, float, str]]:
        return self.store.search(query, k=k)

    def ask(self, question: str, k: int = 3) -> dict[str, object]:
        """Return top-k contexts and a naive extractive answer (longest token overlap)."""
        hits = self.search(question, k=k)
        best_answer = ""
        q_toks = set(_tokenize(question))
        best_score = -1
        for _, _, text in hits:
            t_toks = _tokenize(text)
            overlap = [t for t in t_toks if t in q_toks]
            if len(overlap) > best_score:
                best_score = len(overlap)
                best_answer = " ".join(overlap) if overlap else text[:80]
        return {"answer": best_answer, "hits": hits}
