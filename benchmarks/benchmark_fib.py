from __future__ import annotations

import time

from python_mastery_portfolio.algorithms import fibonacci


def run() -> dict[str, float]:
    start = time.perf_counter()
    for _n in range(1_000):
        fibonacci(20)
    elapsed = (time.perf_counter() - start) * 1000
    return {"iterations": 1000, "ms": elapsed}


if __name__ == "__main__":
    print(run())
