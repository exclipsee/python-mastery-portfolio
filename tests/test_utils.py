from __future__ import annotations

import re

import pytest

from python_mastery_portfolio.utils import timeit, timer


def test_timer_prints_elapsed_time(capsys: pytest.CaptureFixture[str]) -> None:
    with timer("work"):
        pass
    out = capsys.readouterr().out
    assert re.search(r"work took \d+\.\d{2} ms", out)


def test_timeit_decorator(capsys: pytest.CaptureFixture[str]) -> None:
    @timeit
    def add(a: int, b: int) -> int:
        return a + b

    result = add(2, 3)
    assert result == 5
    out = capsys.readouterr().out
    assert re.search(r"add took \d+\.\d{2} ms", out)
