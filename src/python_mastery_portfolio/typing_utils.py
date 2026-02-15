"""Advanced typing utilities."""

from __future__ import annotations

from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")
V = TypeVar("V")


@runtime_checkable
class Serializable(Protocol[T]):
    """Protocol for serializable objects."""
    def to_dict(self) -> dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> T: ...


class Container(Generic[T]):
    """Generic type-safe container."""

    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value

    def map(self, func: Callable[[T], U]) -> Container[U]:
        return Container(func(self.value))


class Result(Generic[T, U]):
    """Success/failure result type."""

    def __init__(self, value: T | None = None, error: U | None = None) -> None:
        if value is not None and error is not None:
            raise ValueError("Cannot have both value and error")
        self.value = value
        self.error = error

    @classmethod
    def success(cls, value: T) -> Result[T, U]:
        return cls(value=value)

    @classmethod
    def failure(cls, error: U) -> Result[T, U]:
        return cls(error=error)

    def is_success(self) -> bool:
        return self.error is None

    def is_failure(self) -> bool:
        return self.error is not None

    def get_or_raise(self) -> T:
        if self.is_success():
            return self.value
        raise ValueError(f"Result is failure: {self.error}")


class Pipeline(Generic[T]):
    """Fluent pipeline for chaining transformations."""

    def __init__(self, initial_value: T) -> None:
        self.value = initial_value
        self.transforms: list[Callable] = []

    def add(self, func: Callable[[T], T]) -> Pipeline[T]:
        self.transforms.append(func)
        return self

    def execute(self) -> T:
        result = self.value
        for func in self.transforms:
            result = func(result)
        return result


from collections.abc import Callable

