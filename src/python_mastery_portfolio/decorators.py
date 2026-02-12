"""Advanced decorator patterns for common use cases."""

from __future__ import annotations

import asyncio
import functools
import logging
import time
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any, Generic, ParamSpec, TypeVar

from .exceptions import RateLimitError, ValidationError

logger = logging.getLogger("decorators")

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")


class RateLimiter:
    """Thread-safe rate limiter using token bucket algorithm."""

    def __init__(self, calls: int, period: float) -> None:
        """
        Initialize RateLimiter.

        Args:
            calls: Number of calls allowed in period
            period: Time period in seconds
        """
        self.calls = calls
        self.period = period
        self.calls_made: list[float] = []
        self.lock = asyncio.Lock()

    async def _try_acquire(self) -> None:
        """Acquire a token, raising RateLimitError if limit exceeded."""
        async with self.lock:
            now = time.time()
            # Remove old timestamps outside the period
            self.calls_made = [t for t in self.calls_made if now - t < self.period]

            if len(self.calls_made) >= self.calls:
                oldest = self.calls_made[0]
                retry_after = self.period - (now - oldest)
                raise RateLimitError(
                    f"Rate limit exceeded: {self.calls} calls per {self.period}s",
                    retry_after=retry_after,
                    limit=self.calls,
                )

            self.calls_made.append(now)

    def reset(self) -> None:
        """Reset rate limiter."""
        self.calls_made.clear()


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator for retrying a function with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for exponential backoff
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated function

    Example:
        @retry(max_attempts=3, delay=1.0, exceptions=(IOError, ConnectionError))
        def unstable_operation():
            ...
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            current_delay = delay
            last_exc: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}"
                        )

            raise last_exc or Exception(f"Failed after {max_attempts} attempts")

        return wrapper

    return decorator


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, Any]], Callable[P, Any]]:
    """
    Decorator for retrying an async function with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for exponential backoff
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated async function
    """

    def decorator(func: Callable[P, Any]) -> Callable[P, Any]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            current_delay = delay
            last_exc: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Async attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}"
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff

            raise last_exc or Exception(f"Async failed after {max_attempts} attempts")

        return wrapper

    return decorator


def timed(
    unit: str = "seconds",
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to measure function execution time.

    Args:
        unit: Time unit for logging ('seconds', 'ms', 'us')

    Returns:
        Decorated function

    Example:
        @timed(unit='ms')
        def slow_function():
            ...
    """
    divisor = {"seconds": 1.0, "ms": 1000.0, "us": 1_000_000.0}.get(unit, 1.0)

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * divisor
            logger.info(f"{func.__name__} executed in {elapsed:.3f} {unit}")
            return result

        return wrapper

    return decorator


def validate_types(**type_checks: type[Any]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to validate argument types at runtime.

    Args:
        **type_checks: Mapping of argument names to expected types

    Returns:
        Decorated function

    Example:
        @validate_types(name=str, age=int)
        def create_user(name: str, age: int):
            ...
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            all_args = {**kwargs}
            sig = inspect_signature(func)

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
    """Descriptor for lazy-loaded, cached properties."""

    def __init__(self, func: Callable[[Any], T]) -> None:
        """
        Initialize CachedProperty.

        Args:
            func: Property getter function
        """
        self.func = func
        self.attr_name = f"_cached_{func.__name__}"

    def __get__(self, obj: Any, objtype: type[Any] | None = None) -> T:
        """Get cached value or compute and cache."""
        if obj is None:
            return self  # type: ignore

        if not hasattr(obj, self.attr_name):
            setattr(obj, self.attr_name, self.func(obj))

        return getattr(obj, self.attr_name)


@contextmanager
def measure_block(name: str = "block") -> Any:
    """
    Context manager to measure execution time of a code block.

    Args:
        name: Name of the block for logging

    Yields:
        None

    Example:
        with measure_block("data_processing"):
            process_data()
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info(f"Block '{name}' executed in {elapsed:.3f} seconds")


def inspect_signature(func: Callable[..., Any]) -> Any:
    """Get function signature for argument inspection."""
    import inspect

    return inspect.signature(func)

