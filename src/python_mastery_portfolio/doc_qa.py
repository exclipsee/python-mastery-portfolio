from __future__ import annotations

import math
import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Protocol


def _tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[A-Za-z0-9']+", text.lower()) if t]


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...

    def dim(self) -> int: ...


class SimpleEmbedder:
    """Deterministic bag-of-words embedder for tests and demo.

    Maintains a growing vocabulary across calls; earlier vectors are padded
    to new size by the index.
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
        for t, vec in zip(texts, embs, strict=True):
            fitted = self._fit_dim(vec, self._dim)
            self._entries.append(_Entry(id=self._next_id, text=t, emb=fitted))
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


def _chunk_text(text: str, *, max_chars: int, overlap: int) -> list[tuple[int, int, str]]:
    """Chunk text into overlapping windows.

    Returns a list of (start, end, chunk_text) tuples.
    """
    if max_chars <= 0:
        return [(0, len(text), text)]
    if overlap < 0:
        overlap = 0

    clean = text.strip("\ufeff")
    if not clean:
        return []

    out: list[tuple[int, int, str]] = []
    start = 0
    n = len(clean)
    while start < n:
        end = min(n, start + max_chars)
        # Prefer to end on a paragraph/sentence boundary when possible
        window = clean[start:end]
        cut = max(window.rfind("\n\n"), window.rfind(". "), window.rfind("\n"))
        if cut >= max(0, len(window) - 200):
            end = start + cut + (2 if window[cut:cut + 2] == ". " else 1)
            end = min(end, n)
            window = clean[start:end]

        chunk = window.strip()
        if chunk:
            out.append((start, end, chunk))

        if end >= n:
            break
        start = max(0, end - overlap)
    return out


# Optional advanced components -------------------------------------------------

class SentenceTransformerEmbedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)
        d = self.model.get_sentence_embedding_dimension()
        if isinstance(d, int):
            self._dim = d
        else:
            # Fallback if API returns an unexpected type
            self._dim = int(d or 0)

    def dim(self) -> int:
        return self._dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        vecs = self.model.encode(texts, normalize_embeddings=True)
        return [list(map(float, v)) for v in vecs]


class FaissIndex:
    def __init__(self, embedder: Embedder) -> None:
        self.embedder = embedder
        self._texts: list[str] = []
        self._ids: list[int] = []
        self._next_id = 1
        self._dim = embedder.dim()
        # Lazily type-annotate FAISS index as Any to satisfy static checkers
        import faiss

        self._faiss: Any = faiss.IndexFlatIP(self._dim)

    def _rebuild_index(self) -> None:
        """Rebuild FAISS index when embedding dimension changes or after reset."""
        import faiss
        import numpy as np

        self._dim = self.embedder.dim()
        self._faiss = faiss.IndexFlatIP(self._dim)
        if not self._texts:
            return
        vecs = self.embedder.embed(self._texts)
        arr = np.asarray(vecs, dtype="float32")
        norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
        arr = arr / norms
        # pyright: ignore[reportGeneralTypeIssues] for FAISS type shims
        self._faiss.add(arr)  # pyright: ignore[reportGeneralTypeIssues]

    def add(self, texts: list[str]) -> list[int]:
        import numpy as np

        # Generate ids and update local stores first
        ids: list[int] = []
        for t in texts:
            self._texts.append(t)
            self._ids.append(self._next_id)
            ids.append(self._next_id)
            self._next_id += 1

        # Compute embeddings for new texts
        vecs = self.embedder.embed(texts)
        new_dim = self.embedder.dim()
        if new_dim != self._dim:
            # Dimension changed (e.g., vocabulary grew). Rebuild entire index.
            self._rebuild_index()
            return ids

        # normalize for cosine similarity on inner product index
        arr = np.asarray(vecs, dtype="float32")
        norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
        arr = arr / norms
        self._faiss.add(arr)  # pyright: ignore[reportGeneralTypeIssues]
        return ids

    def reset(self) -> None:
        self._texts.clear()
        self._ids.clear()
        self._next_id = 1
        # Recreate FAISS index with current embedder dimension
        self._rebuild_index()

    def search(self, query: str, k: int) -> list[tuple[int, float, str]]:
        import numpy as np

        if not self._texts or k <= 0:
            return []

        v = self.embedder.embed([query])[0]
        arr = np.asarray([v], dtype="float32")
        arr = arr / (np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12)
        scores, idxs = self._faiss.search(arr, k)  # pyright: ignore[reportGeneralTypeIssues]
        out: list[tuple[int, float, str]] = []
        # FAISS returns positions in the order vectors were added
        for rank, pos in enumerate(idxs[0]):
            if pos == -1:
                continue
            id_ = self._ids[pos]
            score = float(scores[0][rank])
            out.append((id_, score, self._texts[pos]))
        return out


# Service ---------------------------------------------------------------------


@dataclass(frozen=True)
class QADocument:
    """Structured document for ingestion.

    This mirrors connector output (id/text/metadata) and allows chunked indexing.
    """

    id: str
    text: str
    metadata: dict[str, object]


@dataclass(frozen=True)
class RichHit:
    id: int
    score: float
    text: str
    meta: dict[str, object] | None


class QAService:
    def __init__(self, embedder: Embedder | None = None, index: Index | None = None) -> None:
        self.embedder: Embedder = embedder or SimpleEmbedder()
        self.index: Index = index or NaiveIndex(self.embedder)
        # Stored texts that are actually indexed (documents or chunks)
        self._docs: list[str] = []
        # Metadata aligned with _docs in insertion order
        self._docs_meta: list[dict[str, object] | None] = []
        # Lookup by current index id
        self._id_meta: dict[int, dict[str, object]] = {}

    def add(self, docs: Iterable[str]) -> list[int]:
        ds = list(docs)
        self._docs.extend(ds)
        self._docs_meta.extend([None] * len(ds))
        return self.index.add(ds)

    def add_documents(
        self,
        docs: Iterable[QADocument],
        *,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
    ) -> list[int]:
        """Ingest structured documents with chunking and metadata."""
        to_add: list[str] = []
        pending_meta: list[dict[str, object]] = []
        for doc in docs:
            chunks = _chunk_text(doc.text, max_chars=chunk_size, overlap=chunk_overlap)
            if not chunks:
                continue
            for chunk_index, (start, end, chunk_text) in enumerate(chunks):
                to_add.append(chunk_text)
                pending_meta.append(
                    {
                        "doc_id": doc.id,
                        "chunk_index": chunk_index,
                        "start": start,
                        "end": end,
                        "source": doc.metadata,
                    }
                )

        if not to_add:
            return []

        self._docs.extend(to_add)
        self._docs_meta.extend(pending_meta)
        ids = self.index.add(to_add)
        for id_, meta in zip(ids, pending_meta, strict=True):
            self._id_meta[id_] = meta
        return ids

    def reset(self) -> None:
        self._docs.clear()
        self._docs_meta.clear()
        self._id_meta.clear()
        self.index.reset()

    def search(self, query: str, k: int = 5) -> list[tuple[int, float, str]]:
        return self.index.search(query, k=k)

    def search_rich(self, query: str, k: int = 5) -> list[RichHit]:
        hits = self.search(query, k=k)
        return [RichHit(id=id_, score=score, text=text, meta=self._id_meta.get(id_)) for id_, score, text in hits]

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

    def ask_rich(self, question: str, k: int = 3) -> dict[str, object]:
        hits = self.search_rich(question, k=k)
        best_answer = ""
        q_toks = set(_tokenize(question))
        best_score = -1
        for hit in hits:
            t_toks = _tokenize(hit.text)
            overlap = [t for t in t_toks if t in q_toks]
            if len(overlap) > best_score:
                best_score = len(overlap)
                best_answer = " ".join(overlap) if overlap else hit.text[:80]
        payload_hits = [
            {"id": h.id, "score": h.score, "text": h.text, "meta": h.meta} for h in hits
        ]
        return {"answer": best_answer, "hits": payload_hits}

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
        self._id_meta.clear()
        if self._docs:
            new_ids = self.index.add(list(self._docs))
            for new_id, meta in zip(new_ids, self._docs_meta, strict=True):
                if meta is not None:
                    self._id_meta[new_id] = meta
