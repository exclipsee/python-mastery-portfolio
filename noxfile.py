from __future__ import annotations

import nox


@nox.session
def tests(session: nox.Session) -> None:
    session.install("-e", ".[dev]")
    session.run("pytest")


@nox.session
def lint(session: nox.Session) -> None:
    session.install("-e", ".[dev]")
    session.run("ruff", "check", ".")
    session.run("black", "--check", ".")


@nox.session
def typecheck(session: nox.Session) -> None:
    session.install("-e", ".[dev]")
    session.run("mypy")
