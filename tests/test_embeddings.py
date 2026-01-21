import numpy as np
import pytest

from python_mastery_portfolio.embeddings import (
    SentenceTransformerEmbedder,
    SimpleEmbedder,
)


def test_simple_embedder_fallback_deterministic() -> None:
    emb = SimpleEmbedder(dim=32, ngram_range=(2, 3), use_sklearn=False)
    v1 = emb.embed("hello world")
    v2 = emb.embed("hello world")
    assert v1.shape == (32,)
    assert np.allclose(v1, v2)
    v3 = emb.embed("different text")
    assert v3.shape == (32,)
    assert not np.allclose(v1, v3)


def test_simple_embedder_sklearn_optional() -> None:
    # Skip this test when scikit-learn is not installed in the environment.
    pytest.importorskip("sklearn")
    emb = SimpleEmbedder(dim=16, ngram_range=(2, 3), use_sklearn=True)
    texts = ["a b c", "b c d", "c d e"]
    emb.fit(texts)
    arr = emb.embed_batch(texts)
    assert arr.shape == (3, 16)


def test_sentence_transformer_wrapper_optional() -> None:
    # Skip if sentence-transformers is not installed in the environment.
    pytest.importorskip("sentence_transformers")
    emb = SentenceTransformerEmbedder()
    v = emb.embed("test")
    assert isinstance(v, (list, np.ndarray))
    assert len(v) > 0
