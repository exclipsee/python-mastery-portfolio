from __future__ import annotations

from collections.abc import Sequence


def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("n must be >= 0")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def binary_search(seq: Sequence[int], value: int) -> int:
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
    a, b = int(a), int(b)
    a, b = abs(a), abs(b)
    if a == 0 and b == 0:
        raise ValueError("gcd(0, 0) is undefined")
    while b:
        a, b = b, a % b
    return a


def fibonacci_fast(n: int) -> int:
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
