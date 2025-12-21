from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def _load_toml(path: Path) -> Dict[str, Any]:
    # Prefer stdlib tomllib (Py3.11+), fall back to tomli if available.
    try:
        import tomllib as _tomllib  # type: ignore
    except Exception:
        try:
            import tomli as _tomllib  # type: ignore
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError(
                "TOML support is unavailable; install 'tomli' or use JSON config"
            ) from exc
    return _tomllib.loads(path.read_bytes())


def load_config(path: str | Path) -> Dict[str, Any]:
    """Load a configuration file and return a dict.

    Supported formats: TOML (preferred) and JSON. For TOML support on Python <3.11,
    install the `tomli` package.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {p}")
    if p.suffix.lower() in {".toml"}:
        return _load_toml(p)
    # Default to JSON for other extensions
    return json.loads(p.read_text(encoding="utf-8"))
from __future__ import annotations

from pathlib import Path
from typing import Any


def _load_toml_bytes(data: bytes) -> dict[str, Any]:
    # Try stdlib tomllib (Py3.11+), then tomli backport.
    try:
        import tomllib  # type: ignore

        return tomllib.loads(data.decode("utf-8"))
    except Exception:
        pass
    try:
        import tomli  # type: ignore

        return tomli.loads(data)
    except Exception:
        pass
    raise RuntimeError("TOML support not available (install 'tomli' for Python<3.11)")


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a small TOML config file and return a dict.

    This loader is intentionally lightweight and optional. If TOML parsing
    libraries are not available a RuntimeError is raised.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {p}")
    data = p.read_bytes()
    return _load_toml_bytes(data)
