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


def gcd(a: int, b: int) -> int:
    """Compute the greatest common divisor (GCD) of two integers.

    Uses the iterative Euclidean algorithm. The result is always non-negative.

    Args:
        a: An integer.
        b: Another integer.

    Returns:
        The greatest common divisor of `a` and `b` as a non-negative int.

    Raises:
        ValueError: If both `a` and `b` are zero (GCD undefined).
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

    Fast-doubling computes F(n) in O(log n) time by recursively computing
    (F(k), F(k+1)) and combining results.

    Args:
        n: Index (0 => 0, 1 => 1, ...). Must be >= 0.

    Returns:
        The n-th Fibonacci number as an int.

    Raises:
        ValueError: If n < 0.
    """
    if n < 0:
        raise ValueError("n must be >= 0")

    def _fd(k: int) -> tuple[int, int]:
        if k == 0:
            return 0, 1
        a, b = _fd(k // 2)
        c = a * ((b << 1) - a)  # c = F(2k) = F(k) * (2*F(k+1) - F(k))
        d = a * a + b * b  # d = F(2k+1) = F(k)^2 + F(k+1)^2
        if k & 1:
            return d, c + d
        return c, d

    return _fd(n)[0]
