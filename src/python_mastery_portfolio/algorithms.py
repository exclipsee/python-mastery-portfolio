"""Utility algorithms used by examples and tests.

Small, well-tested algorithms: Fibonacci (iterative and fast doubling),
binary search and gcd helpers. These functions are intentionally
simple and intended for educational/demo use.
"""

from __future__ import annotations

from collections.abc import Sequence


def fibonacci(n: int) -> int:
    """Return the n-th Fibonacci number (0-indexed).

    Args:
        n: Non-negative index of the Fibonacci sequence.

    Returns:
        The n-th Fibonacci integer.

    Raises:
        ValueError: if ``n`` is negative.
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def binary_search(seq: Sequence[int], value: int) -> int:
    """Perform binary search on a sorted sequence.

    Args:
        seq: Sequence of integers (must be sorted in ascending order).
        value: Value to search for.

    Returns:
        Index of ``value`` in ``seq`` if found, otherwise ``-1``.
    """
    lo, hi = 0, len(seq) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if seq[mid] == value:
            return mid
        if seq[mid] < value:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def gcd(a: int, b: int) -> int:
    """Compute the greatest common divisor using Euclid's algorithm.

    Args:
        a: First integer.
        b: Second integer.

    Returns:
        The non-negative greatest common divisor of ``a`` and ``b``.

    Raises:
        ValueError: if both ``a`` and ``b`` are zero (gcd undefined).
    """
    a, b = int(a), int(b)
    a, b = abs(a), abs(b)
    if a == 0 and b == 0:
        raise ValueError("gcd(0, 0) is undefined")
    while b:
        a, b = b, a % b
    return a


def fibonacci_fast(n: int) -> int:
    """Return the n-th Fibonacci number using the fast-doubling method.

    This implementation runs in O(log n) time and avoids linear iteration.

    Args:
        n: Non-negative index of the Fibonacci sequence.

    Returns:
        The n-th Fibonacci integer.

    Raises:
        ValueError: if ``n`` is negative.
    """
    if n < 0:
        raise ValueError("n must be >= 0")

    def _fd(k: int) -> tuple[int, int]:
        if k == 0:
            return 0, 1
        a, b = _fd(k // 2)
        c = a * ((b << 1) - a)
        d = a * a + b * b
        if k & 1:
            return d, c + d
        return c, d

    return _fd(n)[0]
