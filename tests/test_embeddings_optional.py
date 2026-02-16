from __future__ import annotations

import numpy as np

from python_mastery_portfolio.embeddings import SimpleEmbedder


def test_simple_embedder_fallback():
    se = SimpleEmbedder(dim=16, use_sklearn=False)
    v1 = se.embed("hello world")
    v2 = se.embed("hello world")
    assert isinstance(v1, np.ndarray)
    assert v1.shape[0] == 16
    # Deterministic across calls
    assert np.allclose(v1, v2)


def test_simple_embedder_transform_batch():
    se = SimpleEmbedder(dim=8, use_sklearn=False)
    arr = se.embed_batch(["a", "b", "c"])
    assert arr.shape == (3, 8)

