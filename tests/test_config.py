from __future__ import annotations

from pathlib import Path

from python_mastery_portfolio.config import load_config


def test_load_json(tmp_path: Path) -> None:
    p = tmp_path / "cfg.json"
    p.write_text('{"name": "test", "value": 1}', encoding="utf-8")
    cfg = load_config(p)
    assert cfg["name"] == "test"
    assert cfg["value"] == 1


def test_load_toml(tmp_path: Path) -> None:
    p = tmp_path / "cfg.toml"
    p.write_text('name = "toml-test"\nvalue = 2', encoding="utf-8")
    cfg = load_config(p)
    assert cfg["name"] == "toml-test"
    assert int(cfg["value"]) == 2


def test_missing_file_raises(tmp_path: Path) -> None:
    p = tmp_path / "nope.toml"
    try:
        load_config(p)
    except FileNotFoundError:
        return
    raise AssertionError("expected FileNotFoundError")
