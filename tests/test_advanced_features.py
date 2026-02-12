"""Tests for advanced Python features."""

from __future__ import annotations

import asyncio
import time
from typing import Any

import pytest

from python_mastery_portfolio.caching import (
    AsyncLRUCache,
    LRUCache,
    async_cache,
    cache,
)
from python_mastery_portfolio.decorators import (
    CachedProperty,
    async_retry,
    measure_block,
    retry,
    timed,
    validate_types,
)
from python_mastery_portfolio.di_container import (
    DIContainer,
    LifecycleScope,
    ServiceProvider,
    get_container,
    reset_container,
)
from python_mastery_portfolio.exceptions import (
    APIError,
    ConfigurationError,
    DataProcessingError,
    PortfolioError,
    RateLimitError,
    ValidationError,
)
from python_mastery_portfolio.typing_utils import (
    Container,
    Pipeline,
    Result,
    TypedDict,
)


class TestExceptions:
    """Test custom exception hierarchy."""

    def test_portfolio_error_creation(self) -> None:
        """Test creating PortfolioError."""
        err = PortfolioError("Test error", error_code="TEST_001", context={"key": "value"})
        assert err.message == "Test error"
        assert err.error_code == "TEST_001"
        assert err.context == {"key": "value"}

    def test_validation_error(self) -> None:
        """Test ValidationError with field info."""
        err = ValidationError("Invalid age", field="age", value=-5)
        assert err.error_code == "VALIDATION_ERROR"
        assert err.context["field"] == "age"
        assert err.context["value"] == -5

    def test_rate_limit_error(self) -> None:
        """Test RateLimitError."""
        err = RateLimitError("Too many requests", retry_after=60.0, limit=100)
        assert err.error_code == "RATE_LIMIT_EXCEEDED"
        assert err.context["retry_after"] == 60.0
        assert err.context["limit"] == 100

    def test_error_to_dict(self) -> None:
        """Test converting error to dictionary."""
        err = ConfigurationError("Missing config", config_key="API_KEY")
        error_dict = err.to_dict()
        assert error_dict["error_code"] == "CONFIG_ERROR"
        assert error_dict["message"] == "Missing config"
        assert error_dict["context"]["config_key"] == "API_KEY"

    def test_data_processing_error(self) -> None:
        """Test DataProcessingError with processing context."""
        err = DataProcessingError("Failed to parse", step="parsing", row_index=42)
        assert err.context["step"] == "parsing"
        assert err.context["row_index"] == 42


class TestDecorators:
    """Test decorator patterns."""

    def test_retry_success(self) -> None:
        """Test retry decorator on successful function."""
        call_count = 0

        @retry(max_attempts=3)
        def successful_func() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_with_backoff(self) -> None:
        """Test retry with exponential backoff."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01, backoff=2.0, exceptions=(ValueError,))
        def flaky_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = flaky_func()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_async_retry(self) -> None:
        """Test async retry decorator."""
        call_count = 0

        @async_retry(max_attempts=3, delay=0.01, exceptions=(RuntimeError,))
        async def async_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RuntimeError("Async failure")
            return "async success"

        result = await async_func()
        assert result == "async success"
        assert call_count == 2

    def test_timed_decorator(self, capsys: Any) -> None:
        """Test timed decorator."""

        @timed(unit="ms")
        def slow_func() -> None:
            time.sleep(0.01)

        slow_func()
        # Should log timing information

    def test_validate_types_decorator(self) -> None:
        """Test validate_types decorator."""

        @validate_types(name=str, age=int)
        def create_user(name: str, age: int) -> str:
            return f"{name}:{age}"

        result = create_user("Alice", 30)
        assert result == "Alice:30"

    def test_validate_types_fails(self) -> None:
        """Test validate_types raises on invalid type."""

        @validate_types(name=str, age=int)
        def create_user(name: str, age: int) -> str:
            return f"{name}:{age}"

        with pytest.raises(ValidationError):
            create_user("Alice", "not_an_int")

    def test_cached_property_descriptor(self) -> None:
        """Test CachedProperty descriptor."""

        class Computer:
            def __init__(self, value: int) -> None:
                self.value = value
                self.compute_count = 0

            @CachedProperty
            def expensive_property(self) -> int:
                self.compute_count += 1
                return self.value * 2

        comp = Computer(5)
        assert comp.expensive_property == 10
        assert comp.compute_count == 1
        # Second access should use cache
        assert comp.expensive_property == 10
        assert comp.compute_count == 1

    def test_measure_block_context(self) -> None:
        """Test measure_block context manager."""
        with measure_block("test_block"):
            time.sleep(0.01)
        # Should log timing information


class TestCaching:
    """Test caching patterns."""

    def test_lru_cache_basic(self) -> None:
        """Test basic LRU cache operations."""
        cache: LRUCache[str, int] = LRUCache(maxsize=2)

        cache.set("a", 1)
        cache.set("b", 2)
        assert cache.get("a") == 1
        assert cache.get("b") == 2

        # Should evict 'a' when adding 'c' since 'b' was accessed more recently
        cache.set("c", 3)
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_lru_cache_ttl(self) -> None:
        """Test LRU cache with TTL."""
        cache: LRUCache[str, int] = LRUCache(maxsize=10, ttl=0.05)

        cache.set("key", 42)
        assert cache.get("key") == 42

        time.sleep(0.06)
        assert cache.get("key") is None

    def test_lru_cache_stats(self) -> None:
        """Test cache statistics."""
        cache: LRUCache[str, int] = LRUCache(maxsize=10)

        cache.set("a", 1)
        cache.get("a")  # hit
        cache.get("b")  # miss
        cache.get("b")  # miss

        stats = cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 2
        assert stats["hit_rate"] == 1 / 3

    def test_cache_decorator(self) -> None:
        """Test cache decorator on function."""
        call_count = 0

        @cache(maxsize=10, ttl=None)
        def expensive_func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        assert expensive_func(5) == 10
        assert call_count == 1

        # Second call should use cache
        assert expensive_func(5) == 10
        assert call_count == 1

        # Different argument should call function
        assert expensive_func(6) == 12
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_async_lru_cache(self) -> None:
        """Test async LRU cache."""
        cache: AsyncLRUCache[str, int] = AsyncLRUCache(maxsize=10)

        await cache.set("key", 42)
        value = await cache.get("key")
        assert value == 42

    @pytest.mark.asyncio
    async def test_async_cache_decorator(self) -> None:
        """Test async cache decorator."""
        call_count = 0

        @async_cache(maxsize=10)
        async def async_func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0)
            return x * 3

        result = await async_func(4)
        assert result == 12
        assert call_count == 1

        result = await async_func(4)
        assert result == 12
        assert call_count == 1


class TestDIContainer:
    """Test dependency injection container."""

    def test_register_and_resolve(self) -> None:
        """Test registering and resolving services."""

        class Database:
            pass

        container = DIContainer()
        container.register(Database)
        instance = container.resolve(Database)
        assert isinstance(instance, Database)

    def test_singleton_scope(self) -> None:
        """Test singleton lifecycle."""

        class Service:
            pass

        container = DIContainer()
        container.register(Service, scope=LifecycleScope.SINGLETON)

        instance1 = container.resolve(Service)
        instance2 = container.resolve(Service)
        assert instance1 is instance2

    def test_transient_scope(self) -> None:
        """Test transient lifecycle."""

        class Service:
            pass

        container = DIContainer()
        container.register(Service, scope=LifecycleScope.TRANSIENT)

        instance1 = container.resolve(Service)
        instance2 = container.resolve(Service)
        assert instance1 is not instance2

    def test_register_instance(self) -> None:
        """Test registering an existing instance."""

        class Database:
            pass

        db_instance = Database()
        container = DIContainer()
        container.register_instance(Database, db_instance)

        resolved = container.resolve(Database)
        assert resolved is db_instance

    def test_service_not_found(self) -> None:
        """Test resolving unregistered service."""

        class Service:
            pass

        container = DIContainer()
        with pytest.raises(KeyError):
            container.resolve(Service)

    def test_factory_function(self) -> None:
        """Test custom factory function."""

        class Service:
            def __init__(self, value: int) -> None:
                self.value = value

        def factory() -> Service:
            return Service(42)

        container = DIContainer()
        container.register(Service, factory=factory)

        instance = container.resolve(Service)
        assert instance.value == 42


class TestTypingUtils:
    """Test advanced typing utilities."""

    def test_container_get(self) -> None:
        """Test Container generic."""
        cont: Container[int] = Container(42)
        assert cont.get() == 42

    def test_container_map(self) -> None:
        """Test Container map operation."""
        cont: Container[int] = Container(5)
        result = cont.map(lambda x: x * 2)
        assert result.get() == 10

    def test_result_success(self) -> None:
        """Test Result success case."""
        result: Result[int, str] = Result.success(42)
        assert result.is_success()
        assert not result.is_failure()
        assert result.get_or_raise() == 42

    def test_result_failure(self) -> None:
        """Test Result failure case."""
        result: Result[int, str] = Result.failure("error")
        assert result.is_failure()
        assert not result.is_success()
        with pytest.raises(ValueError):
            result.get_or_raise()

    def test_pipeline_execution(self) -> None:
        """Test Pipeline chaining."""
        pipeline = Pipeline(5)
        result = pipeline.add(lambda x: x * 2).add(lambda x: x + 3).execute()
        assert result == 13

    def test_typed_dict(self) -> None:
        """Test TypedDict wrapper."""
        tdict: TypedDict[str, int] = TypedDict()
        tdict.set("count", 10)
        assert tdict.get("count") == 10
        assert len(tdict) == 1

