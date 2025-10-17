from __future__ import annotations

import pytest

from python_mastery_portfolio.algorithms import binary_search, fibonacci


@pytest.mark.parametrize(
    "n,expected",
    [
        (0, 0),
        (1, 1),
        (2, 1),
        (3, 2),
        (10, 55),
    ],
)
def test_fibonacci(n: int, expected: int) -> None:
    assert fibonacci(n) == expected


def test_fibonacci_negative() -> None:
    with pytest.raises(ValueError):
        fibonacci(-1)


def test_binary_search_found() -> None:
    data = [1, 2, 3, 4, 5, 6]
    assert binary_search(data, 1) == 0
    assert binary_search(data, 6) == 5
    assert binary_search(data, 4) == 3


def test_binary_search_not_found() -> None:
    data = [10, 20, 30]
    assert binary_search(data, 15) == -1
