"""Tests for advanced features."""

import asyncio
import pytest

from python_mastery_portfolio import (
    retry,
    async_retry,
    cache,
    async_cache,
    LRUCache,
    DIContainer,
    LifecycleScope,
    Container,
    Result,
    Pipeline,
    ValidationError,
    RateLimitError,
)


class TestExceptions:
    def test_validation_error(self):
        err = ValidationError("Bad value", field="age", value=-5)
        assert err.error_code == "VALIDATION_ERROR"
        assert err.to_dict()["context"]["field"] == "age"

    def test_rate_limit_error(self):
        err = RateLimitError("Too many", retry_after=60.0)
        assert err.error_code == "RATE_LIMIT_EXCEEDED"


class TestDecorators:
    def test_retry_success(self):
        call_count = 0
        @retry(max_attempts=3)
        def succeed():
            nonlocal call_count
            call_count += 1
            return "ok"
        assert succeed() == "ok"
        assert call_count == 1

    def test_retry_with_backoff(self):
        call_count = 0
        @retry(max_attempts=3, delay=0.01, backoff=2.0)
        def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError()
            return "ok"
        assert fail_then_succeed() == "ok"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_async_retry(self):
        call_count = 0
        @async_retry(max_attempts=2, delay=0.01)
        async def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError()
            return "ok"
        assert await fail_then_succeed() == "ok"
        assert call_count == 2

    def test_validate_types_decorator(self):
        from python_mastery_portfolio import validate_types
        @validate_types(name=str, age=int)
        def create_user(name: str, age: int):
            return f"{name}:{age}"
        assert create_user("Alice", 30) == "Alice:30"
        with pytest.raises(ValidationError):
            create_user("Bob", "not_int")


class TestCaching:
    def test_lru_cache_basic(self):
        cache = LRUCache(maxsize=2)
        cache.set("a", 1)
        cache.set("b", 2)
        assert cache.get("a") == 1
        assert cache.get("b") == 2

    def test_lru_cache_eviction(self):
        cache = LRUCache(maxsize=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        assert cache.get("a") is None
        assert cache.get("b") == 2

    def test_cache_decorator(self):
        call_count = 0
        @cache(maxsize=10)
        def expensive(x: int):
            nonlocal call_count
            call_count += 1
            return x * 2
        assert expensive(5) == 10
        assert call_count == 1
        assert expensive(5) == 10
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_async_cache(self):
        call_count = 0
        @async_cache(maxsize=10)
        async def async_expensive(x: int):
            nonlocal call_count
            call_count += 1
            return x * 3
        assert await async_expensive(4) == 12
        assert call_count == 1
        assert await async_expensive(4) == 12
        assert call_count == 1


class TestDIContainer:
    def test_register_singleton(self):
        class Service:
            pass
        container = DIContainer()
        container.register(Service, scope=LifecycleScope.SINGLETON)
        s1 = container.resolve(Service)
        s2 = container.resolve(Service)
        assert s1 is s2

    def test_register_transient(self):
        class Service:
            pass
        container = DIContainer()
        container.register(Service, scope=LifecycleScope.TRANSIENT)
        s1 = container.resolve(Service)
        s2 = container.resolve(Service)
        assert s1 is not s2

    def test_unregistered_service(self):
        class Service:
            pass
        container = DIContainer()
        with pytest.raises(KeyError):
            container.resolve(Service)


class TestTypingUtils:
    def test_container(self):
        cont: Container[int] = Container(42)
        assert cont.get() == 42
        result = cont.map(lambda x: x * 2)
        assert result.get() == 84

    def test_result_success(self):
        r: Result[int, str] = Result.success(42)
        assert r.is_success()
        assert r.get_or_raise() == 42

    def test_result_failure(self):
        r: Result[int, str] = Result.failure("error")
        assert r.is_failure()
        with pytest.raises(ValueError):
            r.get_or_raise()

    def test_pipeline(self):
        result = Pipeline(5).add(lambda x: x*2).add(lambda x: x+3).execute()
        assert result == 13

