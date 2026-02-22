"""Minimal dependency injection container for lightweight wiring.

Supports transient and singleton lifecycles and simple constructor
auto-wiring based on type annotations. This implementation is intentionally
small and suitable for tests and examples.
"""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class LifecycleScope(Enum):
    """Service lifecycle scope."""

    TRANSIENT = "transient"  # New instance each time
    SINGLETON = "singleton"  # Same instance forever
    SCOPED = "scoped"


class DIContainer:
    """Dependency injection container.

    Usage:
        container = DIContainer()
        container.register(MyService)
        s = container.resolve(MyService)
    """

    def __init__(self) -> None:
        self._services: dict[type, tuple[Callable, LifecycleScope, Any]] = {}

    def register(
        self,
        service_type: type[T],
        factory: Callable | None = None,
        scope: LifecycleScope = LifecycleScope.SINGLETON,
    ) -> DIContainer:
        """Register a service type with an optional factory and lifecycle."""
        factory_func = factory or service_type
        self._services[service_type] = (factory_func, scope, None)
        return self

    def resolve(self, service_type: type[T]) -> T:
        """Resolve a service instance.

        The container will attempt to auto-wire constructor parameters using
        registered types if type annotations are present.
        """
        if service_type not in self._services:
            raise KeyError(f"Service {service_type.__name__} not registered")

        factory, scope, instance = self._services[service_type]

        if scope == LifecycleScope.SINGLETON and instance is not None:
            return instance

        # Auto-wire dependencies
        sig = inspect.signature(factory)
        kwargs: dict[str, Any] = {}
        for param_name, param in sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                try:
                    kwargs[param_name] = self.resolve(param.annotation)
                except KeyError:
                    pass

        new_instance = factory(**kwargs)

        if scope == LifecycleScope.SINGLETON:
            self._services[service_type] = (factory, scope, new_instance)

        return new_instance


_container = DIContainer()


def get_container() -> DIContainer:
    """Return the package-level DI container (singleton)."""
    return _container
