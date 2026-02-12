"""Advanced caching patterns for performance optimization."""

from __future__ import annotations

import asyncio
import functools
import logging
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from typing import Any, Generic, TypeVar

logger = logging.getLogger("caching")

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")


class CacheEntry(Generic[V]):
    """Entry in a cache with TTL support."""

    def __init__(self, value: V, ttl: int | float | None = None) -> None:
        """
        Initialize cache entry.

        Args:
            value: Cached value
            ttl: Time to live in seconds (None = indefinite)
        """
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def access(self) -> V:
        """Access value and update stats."""
        self.access_count += 1
        return self.value


class LRUCache(Generic[K, V]):
    """Thread-safe LRU cache with TTL support."""

    def __init__(self, maxsize: int = 128, ttl: int | float | None = None) -> None:
        """
        Initialize LRUCache.

        Args:
            maxsize: Maximum number of entries
            ttl: Default time to live in seconds
        """
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache: OrderedDict[K, CacheEntry[V]] = OrderedDict()
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: K) -> V | None:
        """Get value from cache."""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None

            entry = self.cache[key]
            if entry.is_expired():
                del self.cache[key]
                self.misses += 1
                return None

            self.cache.move_to_end(key)
            self.hits += 1
            return entry.access()

    def set(self, key: K, value: V, ttl: int | float | None = None) -> None:
        """Set value in cache."""
        with self.lock:
            ttl = ttl or self.ttl
            if key in self.cache:
                del self.cache[key]
            elif len(self.cache) >= self.maxsize:
                self.cache.popitem(last=False)

            self.cache[key] = CacheEntry(value, ttl=ttl)

    def clear(self) -> None:
        """Clear entire cache."""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total = self.hits + self.misses
            hit_rate = self.hits / total if total > 0 else 0.0
            return {
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "size": len(self.cache),
                "maxsize": self.maxsize,
            }

    def __repr__(self) -> str:
        """String representation."""
        return f"LRUCache(size={len(self.cache)}, maxsize={self.maxsize})"


class AsyncLRUCache(Generic[K, V]):
    """Async-safe LRU cache with TTL support."""

    def __init__(self, maxsize: int = 128, ttl: int | float | None = None) -> None:
        """
        Initialize AsyncLRUCache.

        Args:
            maxsize: Maximum number of entries
            ttl: Default time to live in seconds
        """
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache: OrderedDict[K, CacheEntry[V]] = OrderedDict()
        self.lock = asyncio.Lock()
        self.hits = 0
        self.misses = 0

    async def get(self, key: K) -> V | None:
        """Get value from cache."""
        async with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None

            entry = self.cache[key]
            if entry.is_expired():
                del self.cache[key]
                self.misses += 1
                return None

            self.cache.move_to_end(key)
            self.hits += 1
            return entry.access()

    async def set(self, key: K, value: V, ttl: int | float | None = None) -> None:
        """Set value in cache."""
        async with self.lock:
            ttl = ttl or self.ttl
            if key in self.cache:
                del self.cache[key]
            elif len(self.cache) >= self.maxsize:
                self.cache.popitem(last=False)

            self.cache[key] = CacheEntry(value, ttl=ttl)

    async def clear(self) -> None:
        """Clear entire cache."""
        async with self.lock:
            self.cache.clear()


def cache(
    maxsize: int = 128,
    ttl: int | float | None = None,
) -> Callable[[Callable[..., V]], Callable[..., V]]:
    """
    Decorator for caching function results with LRU and TTL.

    Args:
        maxsize: Maximum cache size
        ttl: Time to live in seconds

    Returns:
        Decorated function

    Example:
        @cache(maxsize=256, ttl=3600)
        def expensive_computation(x: int) -> int:
            return x ** 2
    """

    def decorator(func: Callable[..., V]) -> Callable[..., V]:
        cache_store: LRUCache[tuple[Any, ...], V] = LRUCache(maxsize=maxsize, ttl=ttl)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> V:
            # Create cache key from args and kwargs
            cache_key = (args, tuple(sorted(kwargs.items())))

            cached = cache_store.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached

            result = func(*args, **kwargs)
            cache_store.set(cache_key, result)
            return result

        wrapper.cache_clear = cache_store.clear  # type: ignore
        wrapper.cache_stats = cache_store.stats  # type: ignore

        return wrapper

    return decorator


def async_cache(
    maxsize: int = 128,
    ttl: int | float | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for caching async function results.

    Args:
        maxsize: Maximum cache size
        ttl: Time to live in seconds

    Returns:
        Decorated async function
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache_store: AsyncLRUCache[tuple[Any, ...], Any] = AsyncLRUCache(
            maxsize=maxsize, ttl=ttl
        )

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_key = (args, tuple(sorted(kwargs.items())))

            cached = await cache_store.get(cache_key)
            if cached is not None:
                logger.debug(f"Async cache hit for {func.__name__}")
                return cached

            result = await func(*args, **kwargs)
            await cache_store.set(cache_key, result)
            return result

        wrapper.cache_clear = cache_store.clear  # type: ignore

        return wrapper

    return decorator

