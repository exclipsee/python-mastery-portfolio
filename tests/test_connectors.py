from __future__ import annotations

import sqlite3
from pathlib import Path

from python_mastery_portfolio.connectors import FileSystemConnector, SQLiteConnector


def test_filesystem_connector(tmp_path: Path) -> None:
    d = tmp_path / "docs"
    d.mkdir()
    f1 = d / "a.md"
    f1.write_text("Hello world")
    f2 = d / "b.txt"
    f2.write_text("Second file")

    conn = FileSystemConnector(d)
    docs = list(conn.iter_documents())
    assert len(docs) == 2
    ids = {doc.id for doc in docs}
    assert str(f1.resolve()) in ids
    assert str(f2.resolve()) in ids


def test_sqlite_connector(tmp_path: Path) -> None:
    db = tmp_path / "data.db"
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("CREATE TABLE documents (id INTEGER PRIMARY KEY, text TEXT, author TEXT)")
    cur.execute("INSERT INTO documents (text, author) VALUES (?, ?)", ("Doc1", "Alice"))
    cur.execute("INSERT INTO documents (text, author) VALUES (?, ?)", ("Doc2", "Bob"))
    conn.commit()
    conn.close()

    connector = SQLiteConnector(
        db,
        "documents",
        id_col="id",
        text_col="text",
        metadata_cols=["author"],
    )
    docs = list(connector.iter_documents())
    assert len(docs) == 2
    assert docs[0].metadata.get("author") in ("Alice", "Bob")
