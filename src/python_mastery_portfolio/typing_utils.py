"""Advanced typing patterns and utilities for type-safe code."""

from __future__ import annotations

from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")
V = TypeVar("V")


@runtime_checkable
class Serializable(Protocol[T]):
    """Protocol for objects that can be serialized."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> T:
        """Create from dictionary representation."""
        ...


@runtime_checkable
class Cacheable(Protocol):
    """Protocol for objects that can be cached."""

    def cache_key(self) -> str:
        """Return unique cache key."""
        ...

    def time_to_live(self) -> int | None:
        """Return TTL in seconds, None for indefinite."""
        ...


@runtime_checkable
class Validator(Protocol[T]):
    """Protocol for validator objects."""

    def validate(self, value: Any) -> T:
        """Validate and return typed value."""
        ...


class Container(Generic[T]):
    """Generic container for holding typed values."""

    def __init__(self, value: T) -> None:
        """Initialize with value."""
        self.value = value

    def get(self) -> T:
        """Get contained value."""
        return self.value

    def map(self, func: type[U] | Any) -> Container[U]:
        """Transform contained value."""
        if callable(func):
            return Container(func(self.value))
        raise TypeError(f"map requires callable, got {type(func)}")

    def __repr__(self) -> str:
        """String representation."""
        return f"Container({self.value!r})"


class Result(Generic[T, U]):
    """Generic result type for success or failure cases."""

    def __init__(self, value: T | None = None, error: U | None = None) -> None:
        """Initialize Result."""
        if value is not None and error is not None:
            raise ValueError("Cannot have both value and error")
        if value is None and error is None:
            raise ValueError("Must provide either value or error")

        self.value = value
        self.error = error

    @classmethod
    def success(cls, value: T) -> Result[T, U]:
        """Create success result."""
        return cls(value=value)

    @classmethod
    def failure(cls, error: U) -> Result[T, U]:
        """Create failure result."""
        return cls(error=error)

    def is_success(self) -> bool:
        """Check if result is success."""
        return self.error is None

    def is_failure(self) -> bool:
        """Check if result is failure."""
        return self.error is not None

    def map(self, func: Callable[[T], U]) -> Result[U, U]:
        """Transform success value."""
        if self.is_success():
            try:
                return Result.success(func(self.value))
            except Exception as e:
                return Result.failure(e)
        return Result.failure(self.error)

    def get_or_raise(self) -> T:
        """Get value or raise error."""
        if self.is_success():
            return self.value
        raise ValueError(f"Result is failure: {self.error}")

    def __repr__(self) -> str:
        """String representation."""
        if self.is_success():
            return f"Result.success({self.value!r})"
        return f"Result.failure({self.error!r})"


class Pipeline(Generic[T]):
    """Generic pipeline for chaining transformations."""

    def __init__(self, initial_value: T) -> None:
        """Initialize with initial value."""
        self.value = initial_value
        self.transformations: list[Callable[[Any], Any]] = []

    def add(self, func: Callable[[T], T]) -> Pipeline[T]:
        """Add transformation to pipeline."""
        self.transformations.append(func)
        return self

    def execute(self) -> T:
        """Execute all transformations and return result."""
        result = self.value
        for transform in self.transformations:
            result = transform(result)
        return result

    def __repr__(self) -> str:
        """String representation."""
        return f"Pipeline({self.value!r}, {len(self.transformations)} transforms)"


class TypedDict(Generic[K, V]):
    """Type-safe dictionary wrapper."""

    def __init__(self, initial: dict[K, V] | None = None) -> None:
        """Initialize TypedDict."""
        self._data: dict[K, V] = initial or {}

    def set(self, key: K, value: V) -> None:
        """Set key-value pair."""
        self._data[key] = value

    def get(self, key: K, default: V | None = None) -> V | None:
        """Get value by key."""
        return self._data.get(key, default)

    def keys(self) -> list[K]:
        """Get all keys."""
        return list(self._data.keys())

    def values(self) -> list[V]:
        """Get all values."""
        return list(self._data.values())

    def items(self) -> list[tuple[K, V]]:
        """Get all key-value pairs."""
        return list(self._data.items())

    def __len__(self) -> int:
        """Get number of items."""
        return len(self._data)

    def __repr__(self) -> str:
        """String representation."""
        return f"TypedDict({self._data!r})"


from collections.abc import Callable

