from __future__ import annotations

import time

from python_mastery_portfolio.caching import LRUCache


def test_lru_cache_ttl_expiration() -> None:
    cache = LRUCache(maxsize=2, ttl=0.05)
    cache.set("k", 1)
    assert cache.get("k") == 1
    time.sleep(0.06)
    assert cache.get("k") is None

