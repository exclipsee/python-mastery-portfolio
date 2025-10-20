from __future__ import annotations

import math
import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol


def _tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[A-Za-z0-9']+", text.lower()) if t]


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...

    def dim(self) -> int: ...


class SimpleEmbedder:
    """Deterministic bag-of-words embedder for tests and demo.

    Maintains a growing vocabulary across calls; earlier vectors are padded to new size by the index.
    """

    def __init__(self) -> None:
        self.vocab: dict[str, int] = {}

    def dim(self) -> int:
        return len(self.vocab)

    def _ensure_vocab(self, texts: list[str]) -> None:
        for d in texts:
            for tok in _tokenize(d):
                if tok not in self.vocab:
                    self.vocab[tok] = len(self.vocab)

    def _vec(self, text: str, size: int) -> list[float]:
        v = [0.0] * size
        for tok in _tokenize(text):
            idx = self.vocab.get(tok)
            if idx is not None and idx < size:
                v[idx] += 1.0
        return v

    def embed(self, texts: list[str]) -> list[list[float]]:
        self._ensure_vocab(texts)
        size = self.dim()
        return [self._vec(t, size) for t in texts]


def _cosine(a: list[float], b: list[float]) -> float:
    num = sum(x * y for x, y in zip(a, b, strict=True))
    da = math.sqrt(sum(x * x for x in a))
    db = math.sqrt(sum(y * y for y in b))
    if da == 0.0 or db == 0.0:
        return 0.0
    return num / (da * db)


class Index(Protocol):
    def add(self, texts: list[str]) -> list[int]: ...

    def reset(self) -> None: ...

    def search(self, query: str, k: int) -> list[tuple[int, float, str]]: ...


@dataclass
class _Entry:
    id: int
    text: str
    emb: list[float]


class NaiveIndex:
    def __init__(self, embedder: Embedder | None = None) -> None:
        self.embedder: Embedder = embedder or SimpleEmbedder()
        self._entries: list[_Entry] = []
        self._next_id = 1
        self._dim = 0

    def _fit_dim(self, v: list[float], dim: int) -> list[float]:
        if len(v) < dim:
            return v + [0.0] * (dim - len(v))
        if len(v) > dim:
            return v[:dim]
        return v

    def add(self, texts: list[str]) -> list[int]:
        embs = self.embedder.embed(texts)
        # track maximum dimension and fit old entries
        self._dim = max(self._dim, self.embedder.dim())
        for e in self._entries:
            if len(e.emb) < self._dim:
                e.emb = self._fit_dim(e.emb, self._dim)
        ids: list[int] = []
        for t, e in zip(texts, embs, strict=True):
            e = self._fit_dim(e, self._dim)
            self._entries.append(_Entry(id=self._next_id, text=t, emb=e))
            ids.append(self._next_id)
            self._next_id += 1
        return ids

    def reset(self) -> None:
        self._entries.clear()
        self._next_id = 1
        self._dim = 0
        # keep embedder instance as-is

    def search(self, query: str, k: int) -> list[tuple[int, float, str]]:
        q_emb = self.embedder.embed([query])[0]
        q_emb = self._fit_dim(q_emb, self._dim)
        scored = [(e.id, _cosine(q_emb, e.emb), e.text) for e in self._entries]
        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[: max(0, k)]


# Optional advanced components -------------------------------------------------

class SentenceTransformerEmbedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        from sentence_transformers import SentenceTransformer  # type: ignore

        self.model = SentenceTransformer(model_name)
        self._dim = int(self.model.get_sentence_embedding_dimension())

    def dim(self) -> int:  # type: ignore[override]
        return self._dim

    def embed(self, texts: list[str]) -> list[list[float]]:  # type: ignore[override]
        vecs = self.model.encode(texts, normalize_embeddings=True)
        return [list(map(float, v)) for v in vecs]


class FaissIndex:
    def __init__(self, embedder: Embedder) -> None:
        import faiss  # type: ignore

        self.embedder = embedder
        self._texts: list[str] = []
        self._ids: list[int] = []
        self._next_id = 1
        self._dim = embedder.dim()
        self._faiss = faiss.IndexFlatIP(self._dim)

    def add(self, texts: list[str]) -> list[int]:  # type: ignore[override]
        import numpy as np  # type: ignore

        vecs = self.embedder.embed(texts)
        self._dim = self.embedder.dim()
        # normalize for cosine similarity on inner product index
        arr = np.asarray(vecs, dtype="float32")
        norms = (np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12)
        arr = arr / norms
        self._faiss.add(arr)
        ids: list[int] = []
        for t in texts:
            self._texts.append(t)
            self._ids.append(self._next_id)
            ids.append(self._next_id)
            self._next_id += 1
        return ids

    def reset(self) -> None:  # type: ignore[override]
        import faiss  # type: ignore

        self._texts.clear()
        self._ids.clear()
        self._next_id = 1
        self._faiss = faiss.IndexFlatIP(self.embedder.dim())

    def search(self, query: str, k: int) -> list[tuple[int, float, str]]:  # type: ignore[override]
        import numpy as np  # type: ignore

        v = self.embedder.embed([query])[0]
        arr = np.asarray([v], dtype="float32")
        arr = arr / (np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12)
        scores, idxs = self._faiss.search(arr, k)
        out: list[tuple[int, float, str]] = []
        for pos in idxs[0]:
            if pos == -1:
                continue
            id_ = self._ids[pos]
            out.append((id_, float(scores[0][pos]), self._texts[pos]))
        return out


# Service ---------------------------------------------------------------------

class QAService:
    def __init__(self, embedder: Embedder | None = None, index: Index | None = None) -> None:
        self.embedder: Embedder = embedder or SimpleEmbedder()
        self.index: Index = index or NaiveIndex(self.embedder)
        self._docs: list[str] = []

    def add(self, docs: Iterable[str]) -> list[int]:
        ds = list(docs)
        self._docs.extend(ds)
        return self.index.add(ds)

    def reset(self) -> None:
        self._docs.clear()
        self.index.reset()

    def search(self, query: str, k: int = 5) -> list[tuple[int, float, str]]:
        return self.index.search(query, k=k)

    def ask(self, question: str, k: int = 3) -> dict[str, object]:
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

    def configure(self, embedder_name: str, index_name: str) -> None:
        # Instantiate embedder
        if embedder_name == "simple":
            emb: Embedder = SimpleEmbedder()
        elif embedder_name == "st":
            emb = SentenceTransformerEmbedder()  # may raise if not installed
        else:
            raise ValueError("unknown embedder")

        # Instantiate index
        if index_name == "naive":
            idx: Index = NaiveIndex(emb)
        elif index_name == "faiss":
            idx = FaissIndex(emb)  # may raise if faiss not installed
        else:
            raise ValueError("unknown index")

        # replace and rebuild with existing docs
        self.embedder = emb
        self.index = idx
        if self._docs:
            self.index.add(self._docs)
