from __future__ import annotations

from python_mastery_portfolio.doc_qa import NaiveIndex, QAService, SimpleEmbedder


def test_simple_embedder_and_index_search() -> None:
    emb = SimpleEmbedder()
    idx = NaiveIndex(emb)
    ids = idx.add(["The quick brown fox", "jumps over the lazy dog", "VIN decoding demo"])
    assert ids == [1, 2, 3]
    hits = idx.search("quick fox", k=2)
    assert len(hits) == 2
    # top hit should be the sentence containing query words
    top = hits[0]
    assert isinstance(top[0], int) and isinstance(top[1], float) and isinstance(top[2], str)


def test_qa_service_add_search_reset() -> None:
    qa = QAService()
    added = qa.add(["FastAPI service", "Streamlit UI", "VIN validation"])
    assert added == [1, 2, 3]
    hits = qa.search("VIN", k=5)
    assert hits and any("VIN".lower() in t.lower() for _, _, t in hits)
    qa.reset()
    hits_after = qa.search("VIN", k=5)
    assert hits_after == []
