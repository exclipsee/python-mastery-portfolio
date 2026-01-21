from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Document:
    id: str
    text: str
    metadata: dict[str, object]


class Connector(ABC):
    """Abstract connector interface for ingesting documents from a source."""

    @abstractmethod
    def iter_documents(self) -> Iterator[Document]: ...

    def to_jsonl(self, out_path: str | Path) -> Path:
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf8") as f:
            for doc in self.iter_documents():
                f.write(json.dumps(asdict(doc), ensure_ascii=False) + "\n")
        return p


# --- Filesystem connector ----------------------------------------------------


class FileSystemConnector(Connector):
    """Read text files (markdown/plain) from a directory and yield documents.

    Args:
        root: directory to scan
        extensions: list of file extensions to include (e.g. ['.md', '.txt'])
        recursive: whether to recurse into subdirectories
    """

    def __init__(
        self,
        root: str | Path,
        extensions: list[str] | None = None,
        recursive: bool = True,
    ) -> None:
        self.root = Path(root)
        self.extensions = [e.lower() for e in extensions or [".md", ".txt"]]
        self.recursive = recursive

    def iter_documents(self) -> Iterator[Document]:
        if self.recursive:
            files = self.root.rglob("*")
        else:
            files = self.root.glob("*")
        for p in files:
            if not p.is_file():
                continue
            if p.suffix.lower() not in self.extensions:
                continue
            try:
                text = p.read_text(encoding="utf8")
            except Exception:
                # Skip unreadable files
                continue
            metadata: dict[str, object] = {"path": str(p), "name": p.name}
            yield Document(id=str(p.resolve()), text=text, metadata=metadata)


# --- SQLite connector (simple) ----------------------------------------------


class SQLiteConnector(Connector):
    """Simple connector that reads text rows from a SQLite table.

    Args:
        db_path: path to sqlite file
        table: table name containing text
        id_col: column name for id
        text_col: column name containing text
        metadata_cols: optional list of columns to include as metadata
    """

    def __init__(
        self,
        db_path: str | Path,
        table: str,
        id_col: str = "id",
        text_col: str = "text",
        metadata_cols: list[str] | None = None,
    ) -> None:
        self.db_path = str(db_path)
        self.table = table
        self.id_col = id_col
        self.text_col = text_col
        self.metadata_cols = metadata_cols or []

    def iter_documents(self) -> Iterator[Document]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cols = [self.id_col, self.text_col] + self.metadata_cols
        col_sql = ", ".join(cols)
        sql = f"SELECT {col_sql} FROM {self.table}"
        try:
            for row in cur.execute(sql):
                doc_id = str(row[self.id_col])
                text = row[self.text_col]
                meta: dict[str, object] = {c: row[c] for c in self.metadata_cols}
                yield Document(id=doc_id, text=text, metadata=meta)
        finally:
            conn.close()
