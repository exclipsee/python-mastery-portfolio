from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _parse_toml_bytes(data: bytes) -> dict[str, Any]:
    text = data.decode("utf-8")
    try:
        from typing import cast

        import tomllib  # type: ignore

        return cast(dict[str, Any], tomllib.loads(text))
    except Exception:
        pass
    try:
        from typing import cast

        import tomli  # type: ignore

        return cast(dict[str, Any], tomli.loads(text))
    except Exception:
        pass
    raise RuntimeError("TOML parser not available; install 'tomli' for Python<3.11")


def load_config(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {p}")
    data = p.read_bytes()
    if p.suffix.lower() == ".toml":
        return _parse_toml_bytes(data)
    from typing import cast

    return cast(dict[str, Any], json.loads(data.decode("utf-8")))
