"""Small embedding utilities.

Provides a compact `SimpleEmbedder` that uses sklearn TF-IDF when available
and a deterministic hash-based fallback otherwise. Also wraps
`sentence-transformers` when installed.
"""

from __future__ import annotations

import hashlib
import importlib
import math
from collections.abc import Iterable
from typing import Any

# Lazily import numpy to keep optional-dep environments functional.
try:
    np = importlib.import_module("numpy")
except Exception:
    np = None  # type: ignore


def _char_ngrams(text: str, n_min: int, n_max: int) -> list[str]:
    s = text or ""
    grams: list[str] = []
    s_len = len(s)
    for n in range(n_min, n_max + 1):
        if s_len < n:
            continue
        for i in range(0, s_len - n + 1):
            grams.append(s[i : i + n])
    return grams


class SimpleEmbedder:
    """Compact embedder: TF-IDF if available, otherwise deterministic hashing.

    Methods:
        fit(texts): fit internal TF-IDF vectorizer when available.
        transform(texts) -> np.ndarray: return a 2D array (n_texts x dim).
        embed(text) -> np.ndarray: return a 1D array of length `dim`.
    """

    def __init__(self, dim: int = 512, ngram_range: tuple[int, int] = (3, 5), use_sklearn: bool | None = None) -> None:
        self.dim = int(dim)
        self.ngram_range = ngram_range
        self._vectorizer: Any | None = None
        if use_sklearn is None:
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore

                self._vectorizer = TfidfVectorizer(analyzer="char", ngram_range=self.ngram_range)
            except Exception:
                self._vectorizer = None
        elif use_sklearn:
            from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore

            self._vectorizer = TfidfVectorizer(analyzer="char", ngram_range=self.ngram_range)

    def fit(self, texts: Iterable[str]) -> None:
        if self._vectorizer is not None:
            self._vectorizer.fit(list(texts))

    def transform(self, texts: Iterable[str]):
        """Return a 2-D numpy array of embeddings (n_texts x dim).

        Raises:
            ImportError: if numpy is not available in the environment.
        """
        if np is None:
            raise ImportError("numpy is required for embeddings; install it with `pip install numpy`")
        texts_list = list(texts)
        if self._vectorizer is not None:
            arr = self._vectorizer.transform(texts_list).toarray().astype("float32")
            if arr.shape[1] < self.dim:
                out = np.zeros((arr.shape[0], self.dim), dtype="float32")
                out[:, : arr.shape[1]] = arr
                return out
            return arr[:, : self.dim]

        out = np.zeros((len(texts_list), self.dim), dtype="float32")
        for i, t in enumerate(texts_list):
            grams = _char_ngrams(t, self.ngram_range[0], self.ngram_range[1])
            if not grams:
                continue
            vec = np.zeros(self.dim, dtype="float32")
            for g in grams:
                h = int(hashlib.md5(g.encode("utf8")).hexdigest()[:8], 16)
                vec[h % self.dim] += 1.0
            norm = math.sqrt(float((vec**2).sum()))
            if norm > 0:
                vec /= norm
            out[i] = vec
        return out

    def fit_transform(self, texts: Iterable[str]):
        self.fit(texts)
        return self.transform(texts)

    def embed(self, text: str):
        """Return a 1-D embedding vector for ``text`` of length ``dim``."""
        arr = self.transform([text])
        return arr[0]

    def embed_batch(self, texts: Iterable[str]):
        """Return embeddings for an iterable of texts as a 2-D numpy array."""
        return self.transform(texts)


class SentenceTransformerEmbedder:
    """Wrapper for `sentence-transformers` SentenceTransformer.

    This class requires the `sentence-transformers` package. If it's not
    installed, initialisation will raise a RuntimeError with install
    instructions.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        try:
            st_mod = importlib.import_module("sentence_transformers")
            SentenceTransformer = getattr(st_mod, "SentenceTransformer")
            self._model = SentenceTransformer(model_name)
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError(
                "Install the 'rag' extras (sentence-transformers) to use "
                "SentenceTransformerEmbedder"
            ) from exc

    def embed(self, text: str):
        if np is None:
            raise ImportError("numpy is required for embeddings; install it with `pip install numpy`")
        return self._model.encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: Iterable[str]):
        if np is None:
            raise ImportError("numpy is required for embeddings; install it with `pip install numpy`")
        return self._model.encode(list(texts), convert_to_numpy=True)


__all__ = ["SimpleEmbedder", "SentenceTransformerEmbedder"]
