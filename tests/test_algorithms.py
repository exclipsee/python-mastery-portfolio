from __future__ import annotations

import pytest

from python_mastery_portfolio.algorithms import binary_search, fibonacci, gcd


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


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (48, 18, 6),
        (7, 3, 1),
        (0, 5, 5),
        (5, 0, 5),
        (0, -5, 5),
        (-27, 9, 9),
    ],
)
def test_gcd(a: int, b: int, expected: int) -> None:
    assert gcd(a, b) == expected


def test_gcd_both_zero() -> None:
    with pytest.raises(ValueError):
        gcd(0, 0)
