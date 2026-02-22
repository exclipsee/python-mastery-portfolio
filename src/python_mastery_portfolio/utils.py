"""Small runtime utilities: timing decorators and context managers.

These helpers are intended for lightweight benchmarking and debugging; they
log timing information at DEBUG level instead of printing to stdout.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)


def timeit(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator that logs the runtime of ``func`` at DEBUG level.

    The decorator always executes the function and logs elapsed milliseconds
    even if the function raises an exception.
    """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            logger.debug("%s took %.2f ms", func.__name__, elapsed)

    return wrapper


@contextmanager
def timer(label: str) -> Generator[None, None, None]:
    """Context manager that logs the elapsed time for a block.

    Args:
        label: Short label to include in the log message.
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = (time.perf_counter() - start) * 1000
        logger.debug("%s took %.2f ms", label, elapsed)
