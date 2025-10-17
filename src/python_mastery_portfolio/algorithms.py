from __future__ import annotations

from collections.abc import Sequence


def fibonacci(n: int) -> int:
    """Return the n-th Fibonacci number (0-indexed).

    Uses an iterative O(n) time and O(1) space approach.

    Args:
        n: Index (0 => 0, 1 => 1, 2 => 1, ...). Must be >= 0.

    Returns:
        The n-th Fibonacci number as an int.

    Raises:
        ValueError: If n < 0.
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def binary_search(seq: Sequence[int], value: int) -> int:
    """Return index of value in sorted sequence using binary search, or -1 if not found.

    Args:
        seq: A sorted sequence of integers.
        value: The integer value to search for.

    Returns:
        Index of the value if present; otherwise -1.
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
