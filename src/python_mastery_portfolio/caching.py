"""Caching with LRU and TTL.

Small thread-safe and async-safe LRU caches and decorators for function
result caching. The decorators use a tuple key derived from args and a
stable representation of kwargs to avoid issues with unhashable values.
"""

from __future__ import annotations

import asyncio
import functools
import threading
import time
from collections import OrderedDict
from typing import Any, Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class LRUCache(Generic[K, V]):
    """Thread-safe LRU cache with optional TTL (time-to-live in seconds)."""

    def __init__(self, maxsize: int = 128, ttl: int | float | None = None) -> None:
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache: OrderedDict[K, tuple[V, float]] = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key: K) -> V | None:
        with self.lock:
            if key not in self.cache:
                return None
            value, created = self.cache[key]
            if self.ttl and time.time() - created > self.ttl:
                del self.cache[key]
                return None
            self.cache.move_to_end(key)
            return value

    def set(self, key: K, value: V) -> None:
        with self.lock:
            if key in self.cache:
                del self.cache[key]
            elif len(self.cache) >= self.maxsize:
                self.cache.popitem(last=False)
            self.cache[key] = (value, time.time())

    def clear(self) -> None:
        with self.lock:
            self.cache.clear()


class AsyncLRUCache(Generic[K, V]):
    """Async-safe LRU cache with optional TTL."""

    def __init__(self, maxsize: int = 128, ttl: int | float | None = None) -> None:
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache: OrderedDict[K, tuple[V, float]] = OrderedDict()
        self.lock = asyncio.Lock()

    async def get(self, key: K) -> V | None:
        async with self.lock:
            if key not in self.cache:
                return None
            value, created = self.cache[key]
            if self.ttl and time.time() - created > self.ttl:
                del self.cache[key]
                return None
            self.cache.move_to_end(key)
            return value

    async def set(self, key: K, value: V) -> None:
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
            elif len(self.cache) >= self.maxsize:
                self.cache.popitem(last=False)
            self.cache[key] = (value, time.time())

    async def clear(self) -> None:
        async with self.lock:
            self.cache.clear()


def _kwargs_key(kwargs: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    """Create a stable, hashable representation for kwargs using repr for values.

    This avoids TypeError when kwargs have unhashable values (e.g., lists).
    """
    return tuple(sorted((k, repr(v)) for k, v in kwargs.items()))


def cache(maxsize: int = 128, ttl: int | float | None = None) -> Any:
    """Decorator for function result caching (synchronous functions)."""

    def decorator(func: Any) -> Any:
        store: LRUCache[tuple, Any] = LRUCache(maxsize, ttl)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (args, _kwargs_key(kwargs))
            cached = store.get(key)
            if cached is not None:
                return cached
            result = func(*args, **kwargs)
            store.set(key, result)
            return result

        return wrapper

    return decorator


def async_cache(maxsize: int = 128, ttl: int | float | None = None) -> Any:
    """Decorator for async function result caching."""

    def decorator(func: Any) -> Any:
        store: AsyncLRUCache[tuple, Any] = AsyncLRUCache(maxsize, ttl)

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (args, _kwargs_key(kwargs))
            cached = await store.get(key)
            if cached is not None:
                return cached
            result = await func(*args, **kwargs)
            await store.set(key, result)
            return result

        return wrapper

    return decorator

