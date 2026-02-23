"""Advanced typing utilities.

Small collection of convenience generic types and simple functional helpers
used by examples and tests.
"""

from __future__ import annotations

from typing import Any, Generic, Protocol, TypeVar, runtime_checkable
from collections.abc import Callable

T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")
V = TypeVar("V")


@runtime_checkable
class Serializable(Protocol[T]):
    """Protocol for serializable objects.

    Implementers should provide ``to_dict`` and ``from_dict`` methods.
    """

    def to_dict(self) -> dict[str, Any]: ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> T: ...


class Container(Generic[T]):
    """Generic type-safe container wrapping a single value."""

    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        """Return the contained value."""
        return self.value

    def map(self, func: Callable[[T], U]) -> "Container[U]":
        """Transform the contained value with ``func`` and return a new container."""
        return Container(func(self.value))


class Result(Generic[T, U]):
    """Simple success/failure result type.

    Only one of ``value`` or ``error`` may be set.
    """

    def __init__(self, value: T | None = None, error: U | None = None) -> None:
        if value is not None and error is not None:
            raise ValueError("Cannot have both value and error")
        self.value = value
        self.error = error

    @classmethod
    def success(cls, value: T) -> "Result[T, U]":
        return cls(value=value)

    @classmethod
    def failure(cls, error: U) -> "Result[T, U]":
        return cls(error=error)

    def is_success(self) -> bool:
        return self.error is None

    def is_failure(self) -> bool:
        return self.error is not None

    def get_or_raise(self) -> T:
        """Return the value if success, otherwise raise a ValueError."""
        if self.is_success():
            # type: ignore[return-value]
            return self.value
        raise ValueError(f"Result is failure: {self.error}")


class Pipeline(Generic[T]):
    """Fluent pipeline for chaining transformations on a value."""

    def __init__(self, initial_value: T) -> None:
        self.value = initial_value
        self.transforms: list[Callable[[T], T]] = []

    def add(self, func: Callable[[T], T]) -> "Pipeline[T]":
        """Add a transformation function to the pipeline."""
        self.transforms.append(func)
        return self

    def execute(self) -> T:
        """Execute the pipeline and return the transformed value."""
        result = self.value
        for func in self.transforms:
            result = func(result)
        return result
