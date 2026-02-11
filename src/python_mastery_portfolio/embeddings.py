from __future__ import annotations

import hashlib
import math
from collections.abc import Iterable
from typing import Any, cast

import numpy as np


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
    """Compact embedder: TF-IDF if available, otherwise deterministic hashing."""

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

    def transform(self, texts: Iterable[str]) -> np.ndarray:
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

    def fit_transform(self, texts: Iterable[str]) -> np.ndarray:
        self.fit(texts)
        return self.transform(texts)

    def embed(self, text: str) -> np.ndarray:
        return cast(np.ndarray, self.transform([text])[0])

    def embed_batch(self, texts: Iterable[str]) -> np.ndarray:
        return self.transform(texts)


class SentenceTransformerEmbedder:
    """Wrapper for `sentence-transformers` SentenceTransformer.

    This class requires the `sentence-transformers` package. If it's not
    installed, initialisation will raise a RuntimeError with install
    instructions.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(model_name)
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError(
                "Install the 'rag' extras (sentence-transformers) to use "
                "SentenceTransformerEmbedder"
            ) from exc

    def embed(self, text: str) -> np.ndarray:
        import numpy as _np

        return self._model.encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: Iterable[str]) -> np.ndarray:
        import numpy as _np

        return self._model.encode(list(texts), convert_to_numpy=True)


__all__ = ["SimpleEmbedder", "SentenceTransformerEmbedder"]
