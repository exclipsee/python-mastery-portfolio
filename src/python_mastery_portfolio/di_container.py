"""Dependency injection container for managing object lifecycle and dependencies."""

from __future__ import annotations

import functools
import inspect
import logging
from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, TypeVar

logger = logging.getLogger("di_container")

T = TypeVar("T")


class LifecycleScope(Enum):
    """Lifecycle scope for dependencies."""

    TRANSIENT = "transient"  # New instance every time
    SINGLETON = "singleton"  # Same instance forever
    SCOPED = "scoped"  # Same instance within a scope


class ServiceDescriptor(Generic[T]):
    """Descriptor for a registered service."""

    def __init__(
        self,
        service_type: type[T],
        factory: Callable[..., T],
        scope: LifecycleScope = LifecycleScope.SINGLETON,
    ) -> None:
        """
        Initialize ServiceDescriptor.

        Args:
            service_type: Type of service
            factory: Factory function to create service
            scope: Lifecycle scope for service
        """
        self.service_type = service_type
        self.factory = factory
        self.scope = scope
        self.instance: T | None = None

    def get_instance(self, container: DIContainer) -> T:
        """Get or create service instance."""
        if self.scope == LifecycleScope.SINGLETON and self.instance is not None:
            return self.instance

        sig = inspect.signature(self.factory)
        kwargs: dict[str, Any] = {}

        for param_name, param in sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                try:
                    kwargs[param_name] = container.resolve(param.annotation)
                except KeyError:
                    pass

        instance = self.factory(**kwargs)

        if self.scope == LifecycleScope.SINGLETON:
            self.instance = instance

        return instance


class DIContainer:
    """Dependency injection container."""

    def __init__(self) -> None:
        """Initialize DIContainer."""
        self._services: dict[type[Any], ServiceDescriptor[Any]] = {}
        self._scoped_instances: dict[str, Any] = {}

    def register(
        self,
        service_type: type[T],
        factory: Callable[..., T] | None = None,
        scope: LifecycleScope = LifecycleScope.SINGLETON,
    ) -> DIContainer:
        """
        Register a service.

        Args:
            service_type: Type to register
            factory: Factory function (defaults to service_type itself)
            scope: Lifecycle scope

        Returns:
            Self for chaining

        Example:
            container.register(DatabaseService, scope=LifecycleScope.SINGLETON)
            container.register(RequestService, factory=lambda: RequestService())
        """
        factory_func = factory or service_type
        descriptor = ServiceDescriptor(service_type, factory_func, scope=scope)
        self._services[service_type] = descriptor
        logger.debug(f"Registered {service_type.__name__} with scope {scope.value}")
        return self

    def resolve(self, service_type: type[T]) -> T:
        """
        Resolve a service instance.

        Args:
            service_type: Type to resolve

        Returns:
            Service instance

        Raises:
            KeyError: If service not registered
        """
        if service_type not in self._services:
            raise KeyError(f"Service {service_type.__name__} not registered")

        descriptor = self._services[service_type]
        return descriptor.get_instance(self)

    def register_instance(self, service_type: type[T], instance: T) -> DIContainer:
        """
        Register an existing instance as singleton.

        Args:
            service_type: Type to register
            instance: Instance to use

        Returns:
            Self for chaining
        """

        def factory() -> T:
            return instance

        descriptor = ServiceDescriptor(
            service_type, factory, scope=LifecycleScope.SINGLETON
        )
        descriptor.instance = instance
        self._services[service_type] = descriptor
        logger.debug(f"Registered instance of {service_type.__name__}")
        return self

    def clear(self) -> None:
        """Clear all registrations and scoped instances."""
        self._services.clear()
        self._scoped_instances.clear()
        logger.debug("DI container cleared")

    def __repr__(self) -> str:
        """String representation."""
        count = len(self._services)
        return f"DIContainer({count} services registered)"


class ServiceProvider:
    """Decorator-based service provider for easier dependency resolution."""

    def __init__(self, container: DIContainer | None = None) -> None:
        """
        Initialize ServiceProvider.

        Args:
            container: DIContainer to use
        """
        self.container = container or DIContainer()

    def inject(self, service_type: type[T]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to inject dependencies into function.

        Args:
            service_type: Type to inject

        Returns:
            Decorated function

        Example:
            @provider.inject(DatabaseService)
            def process_data(db: DatabaseService):
                ...
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                instance = self.container.resolve(service_type)
                return func(*args, instance, **kwargs)

            return wrapper

        return decorator

    def __repr__(self) -> str:
        """String representation."""
        return f"ServiceProvider({self.container})"


# Global container instance for convenience
_global_container = DIContainer()


def get_container() -> DIContainer:
    """Get global DI container."""
    return _global_container


def reset_container() -> None:
    """Reset global DI container."""
    _global_container.clear()

