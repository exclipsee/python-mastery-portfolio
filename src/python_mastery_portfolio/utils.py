from __future__ import annotations

import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def timeit(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator that prints the runtime of the wrapped function.

    Intended for demonstration; in production you might prefer a structured logger.
    """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            print(f"{func.__name__} took {elapsed:.2f} ms")

    return wrapper


@contextmanager
def timer(label: str) -> Generator[None, None, None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = (time.perf_counter() - start) * 1000
        print(f"{label} took {elapsed:.2f} ms")
