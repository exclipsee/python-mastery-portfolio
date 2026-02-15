"""Core decorators."""

from __future__ import annotations

import asyncio
import functools
import time
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any, Generic, ParamSpec, TypeVar

from .exceptions import ValidationError

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable:
    """Retry with exponential backoff."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            current_delay = delay
            last_exc: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
            raise last_exc or Exception(f"Failed after {max_attempts} attempts")
        return wrapper
    return decorator


def async_retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable:
    """Async retry with exponential backoff."""
    def decorator(func: Callable[P, Any]) -> Callable[P, Any]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            current_delay = delay
            last_exc: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
            raise last_exc or Exception(f"Failed after {max_attempts} attempts")
        return wrapper
    return decorator


def timed(unit: str = "seconds") -> Callable:
    """Measure execution time."""
    divisor = {"seconds": 1.0, "ms": 1000.0, "us": 1_000_000.0}.get(unit, 1.0)
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * divisor
            print(f"{func.__name__} executed in {elapsed:.3f} {unit}")
            return result
        return wrapper
    return decorator


def validate_types(**type_checks: type[Any]) -> Callable:
    """Validate argument types at runtime."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            import inspect
            sig = inspect.signature(func)
            all_args = {**kwargs}
            for i, (param_name, param) in enumerate(sig.parameters.items()):
                if i < len(args):
                    all_args[param_name] = args[i]

            for arg_name, expected_type in type_checks.items():
                if arg_name in all_args:
                    value = all_args[arg_name]
                    if not isinstance(value, expected_type):
                        raise ValidationError(
                            f"Argument {arg_name} must be {expected_type.__name__}",
                            field=arg_name,
                            value=value,
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator


class CachedProperty(Generic[T]):
    """Lazy-loaded cached property."""

    def __init__(self, func: Callable[[Any], T]) -> None:
        self.func = func
        self.attr_name = f"_cached_{func.__name__}"

    def __get__(self, obj: Any, objtype: type[Any] | None = None) -> T:
        if obj is None:
            return self  # type: ignore
        if not hasattr(obj, self.attr_name):
            setattr(obj, self.attr_name, self.func(obj))
        return getattr(obj, self.attr_name)


@contextmanager
def measure_block(name: str = "block") -> Any:
    """Time a code block."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"Block '{name}': {elapsed:.3f}s")

