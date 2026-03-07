"""Bump the version in pyproject.toml (very small helper).

Usage:
    python tools/bump_version.py [major|minor|patch] [--dry-run]

This script updates the version found under [project] -> version or top-level version.
It's intentionally conservative and prints changes instead of doing risky transformations.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

TOML = Path("pyproject.toml")

def read_version(text: str) -> tuple[str, int, int, int]:
    m = re.search(r"version\s*=\s*\"(\d+)\.(\d+)\.(\d+)\"", text)
    if not m:
        raise SystemExit("Could not find a semantic version in pyproject.toml")
    major, minor, patch = map(int, m.groups())
    return m.group(0), major, minor, patch


def write_version(text: str, old_line: str, new_version: str) -> str:
    return text.replace(old_line, f'version = "{new_version}"', 1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("part", choices=["major", "minor", "patch"], nargs="?", default="patch")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    text = TOML.read_text(encoding="utf8")
    old_line, major, minor, patch = read_version(text)
    if args.part == "major":
        major += 1
        minor = 0
        patch = 0
    elif args.part == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    new_version = f"{major}.{minor}.{patch}"
    new_text = write_version(text, old_line, new_version)
    print(f"Old: {old_line}")
    print(f"New: version = \"{new_version}\"")
    if not args.dry_run:
        TOML.write_text(new_text, encoding="utf8")
        print("pyproject.toml updated")

if __name__ == "__main__":
    main()

