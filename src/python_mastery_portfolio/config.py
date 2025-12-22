from __future__ import annotations

from pathlib import Path
from typing import Any
import json


def _parse_toml_bytes(data: bytes) -> dict[str, Any]:
    """Parse TOML from bytes.

    Prefer the stdlib `tomllib` (Python 3.11+). If unavailable, try the
    `tomli` backport. Raise RuntimeError if no TOML parser is available.
    """
    text = data.decode("utf-8")
    try:
        import tomllib  # type: ignore

        return tomllib.loads(text)
    except Exception:
        pass
    try:
        import tomli  # type: ignore

        return tomli.loads(text)
    except Exception:
        pass
    raise RuntimeError("TOML parser not available; install 'tomli' for Python<3.11")


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a small configuration file and return a dictionary.

    Supported formats:
    - TOML: when file extension is `.toml` (preferred). Uses `tomllib` or
      `tomli`.
    - JSON: for other extensions, parsed with the stdlib `json` module.

    Raises `FileNotFoundError` when the path is missing and `RuntimeError`
    when TOML support is requested but not available.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {p}")
    data = p.read_bytes()
    if p.suffix.lower() == ".toml":
        return _parse_toml_bytes(data)
    # Default to JSON for all other extensions
    return json.loads(data.decode("utf-8"))
