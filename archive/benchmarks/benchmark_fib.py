from __future__ import annotations

import argparse
import time
from statistics import mean

from python_mastery_portfolio.algorithms import fibonacci


def run(iterations: int = 1000, n: int = 20, warmup: int = 5) -> dict[str, float]:
    """Run a simple benchmark for `fibonacci(n)`.

    Returns a dict with total elapsed milliseconds and average milliseconds
    per invocation.
    """
    # Warmup
    for _ in range(warmup):
        fibonacci(n)

    timings: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        fibonacci(n)
        timings.append((time.perf_counter() - start) * 1000)

    total_ms = sum(timings)
    avg_ms = mean(timings) if timings else 0.0
    return {"iterations": iterations, "n": n, "total_ms": total_ms, "avg_ms": avg_ms}


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark fibonacci(n) performance")
    parser.add_argument("--iterations", "-i", type=int, default=1000, help="Number of iterations")
    parser.add_argument("--n", "-n", type=int, default=20, help="Fibonacci index to compute")
    parser.add_argument("--warmup", "-w", type=int, default=5, help="Warmup runs before timing")
    args = parser.parse_args()

    result = run(iterations=args.iterations, n=args.n, warmup=args.warmup)
    print(result)


if __name__ == "__main__":
    main()

