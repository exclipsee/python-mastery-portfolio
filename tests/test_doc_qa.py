from __future__ import annotations

from fastapi.testclient import TestClient

from python_mastery_portfolio.api import app


def test_doc_qa_flow() -> None:
    client = TestClient(app)
    # reset store
    r = client.post("/qa/reset")
    assert r.status_code == 200

    # add documents
    docs = [
        "Python is a popular programming language.",
        "FastAPI is a modern, fast (high-performance) web framework for building APIs with Python.",
        "Pandas provides high-performance, easy-to-use data structures and data analysis tools.",
    ]
    r = client.post("/qa/documents", json=docs)
    assert r.status_code == 200
    ids = r.json()["ids"]
    assert len(ids) == 3

    # search
    r = client.post("/qa/search", params={"query": "What is FastAPI?", "k": 2})
    assert r.status_code == 200
    hits = r.json()["hits"]
    assert len(hits) == 2

    # ask
    r = client.post("/qa/ask", params={"question": "What is FastAPI?", "k": 2})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data and isinstance(data["hits"], list)


def test_doc_qa_rich_ingest_and_ask() -> None:
    client = TestClient(app)
    r = client.post(
        "/qa/ingest",
        json={
            "reset": True,
            "chunk_size": 120,
            "chunk_overlap": 10,
            "documents": [
                {"id": "doc1", "text": "FastAPI is a web framework for building APIs.", "metadata": {"src": "a"}},
                {"id": "doc2", "text": "Pandas is used for data analysis.", "metadata": {"src": "b"}},
            ],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["n_chunks"] >= 1

    r = client.post("/qa/search_rich", params={"query": "What is FastAPI?", "k": 3})
    assert r.status_code == 200
    hits = r.json()["hits"]
    assert isinstance(hits, list) and hits
    assert "meta" in hits[0]

    r = client.post("/qa/ask_rich", params={"question": "What is FastAPI?", "k": 2})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert isinstance(data.get("hits"), list)
