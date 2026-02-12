# Getting Started with Advanced Features

## Overview

Your Python mastery portfolio now includes **advanced professional-grade features** that showcase deep expertise. This guide helps you understand what was added and how to use it.

## What's New

### 5 Core Modules

| Module | Purpose | Key Classes/Functions |
|--------|---------|----------------------|
| `exceptions.py` | Structured error handling | `ValidationError`, `RateLimitError`, `PortfolioError` |
| `decorators.py` | Advanced decorator patterns | `@retry`, `@async_retry`, `@timed`, `@cache`, `CachedProperty` |
| `caching.py` | Production caching | `LRUCache`, `AsyncLRUCache`, `@cache`, `@async_cache` |
| `di_container.py` | Dependency injection | `DIContainer`, `LifecycleScope`, `ServiceProvider` |
| `typing_utils.py` | Advanced typing | `Container[T]`, `Result[T, U]`, `Pipeline[T]` |

### Documentation

- **PATTERNS.md** - Detailed explanations of all patterns with examples
- **examples.py** - Real-world usage scenarios
- **This file** - Getting started guide

---

## Installation & Setup

Everything is ready to use! Just import:

```python
# Decorators
from python_mastery_portfolio import retry, async_retry, timed, cache

# Error handling
from python_mastery_portfolio import ValidationError, RateLimitError

# DI Container
from python_mastery_portfolio import DIContainer, LifecycleScope

# Advanced typing
from python_mastery_portfolio import Container, Result, Pipeline

# Caching
from python_mastery_portfolio import LRUCache, async_cache
```

---

## Common Use Cases

### 1. Retry Flaky Operations

```python
@retry(max_attempts=3, delay=1.0, backoff=2.0)
def fetch_from_api():
    # Automatically retried with exponential backoff
    pass
```

### 2. Cache Expensive Results

```python
@cache(maxsize=256, ttl=3600)
def expensive_computation(x: int) -> int:
    # Cached for 1 hour
    return sum(range(x))

# Check cache statistics
print(expensive_computation.cache_stats())
```

### 3. Validate Input with Error Context

```python
from python_mastery_portfolio import ValidationError

if age < 0:
    raise ValidationError(
        "Age cannot be negative",
        field="age",
        value=age
    )
```

### 4. Set Up Dependency Injection

```python
from python_mastery_portfolio import DIContainer, LifecycleScope

container = DIContainer()
container.register(DatabaseService, scope=LifecycleScope.SINGLETON)
container.register(UserService, scope=LifecycleScope.TRANSIENT)

db = container.resolve(DatabaseService)
```

### 5. Use Result Type for Error Handling

```python
from python_mastery_portfolio import Result

def divide(a: int, b: int) -> Result[float, str]:
    if b == 0:
        return Result.failure("Cannot divide by zero")
    return Result.success(a / b)

result = divide(10, 2)
if result.is_success():
    print(result.get_or_raise())
```

---

## Test Coverage

All new features have comprehensive tests:

```bash
# Run all tests
pytest

# Run only new advanced features tests
pytest tests/test_advanced_features.py -v

# Check coverage
pytest --cov=python_mastery_portfolio
```

**Current Coverage**: 75% overall, with new modules at 73-89% coverage

---

## What Makes This Portfolio Strong

### For Interviews
- Demonstrate knowledge of advanced Python patterns
- Explain production-ready error handling
- Discuss async/await patterns and concurrency
- Talk about type safety and generics
- Discuss design patterns (decorator, factory, DI)

### For Real Work
- Production-grade caching with TTL
- Automatic retry with backoff
- Dependency injection for testability
- Type-safe error handling
- Performance optimization patterns

### For Code Review
- Strict mypy type checking
- Comprehensive documentation
- High test coverage
- Clear error contexts
- Thread-safe implementations

---

## Directory Structure

```
python-mastery-portfolio/
├── src/python_mastery_portfolio/
│   ├── __init__.py              # Exports all public APIs
│   ├── exceptions.py            # Custom exception hierarchy
│   ├── decorators.py            # Decorator patterns
│   ├── caching.py               # Caching implementations
│   ├── di_container.py          # DI container
│   ├── typing_utils.py          # Advanced typing utilities
│   ├── examples.py              # Usage examples
│   └── ... (other modules)
├── tests/
│   ├── test_advanced_features.py  # 31 comprehensive tests
│   └── ... (other tests)
├── PATTERNS.md                   # Detailed pattern guide
├── IMPLEMENTATION_SUMMARY.md     # Implementation details
└── README.md                     # Updated with new features
```

---

## Learning Path

1. **Start with Examples**: Read `src/python_mastery_portfolio/examples.py`
2. **Understand Patterns**: Read `PATTERNS.md`
3. **Explore Tests**: Look at `tests/test_advanced_features.py`
4. **Try It Out**: Start using decorators and caching
5. **Deep Dive**: Study each module's source code

---

## Frequently Asked Questions

### Q: How does the DI container work?
The container uses Python's `inspect` module to read function signatures and automatically resolve dependencies. It supports Singleton (same instance), Transient (new instance), and Scoped lifecycles.

### Q: Why use Result type instead of exceptions?
Result types allow functional error handling where errors are data, not control flow. Great for pipelines and transformations.

### Q: How thread-safe is the caching?
Both sync and async caches use proper locks (threading.Lock and asyncio.Lock respectively) to ensure thread-safety and async-safety.

### Q: Can I customize the retry backoff?
Yes! `@retry(max_attempts=5, delay=0.5, backoff=2.0)` lets you control attempts, initial delay, and backoff multiplier.

### Q: How do decorators preserve type hints?
Using `ParamSpec` and `TypeVar`, decorators preserve the original function's signature for better IDE support and type checking.

---

## Advanced Topics

### Thread-Safe vs Async-Safe Caching

The caching module provides both:

```python
from python_mastery_portfolio import LRUCache, AsyncLRUCache

# For sync code (thread-safe)
sync_cache = LRUCache(maxsize=128, ttl=3600)

# For async code (async-safe)
async_cache = AsyncLRUCache(maxsize=128, ttl=3600)
```

### Generic Types

All utilities use proper generics:

```python
from python_mastery_portfolio import Container, Pipeline

# Type-checked container
numbers: Container[int] = Container(42)
result = numbers.map(lambda x: x * 2)

# Type-checked pipeline
output = Pipeline(10).add(lambda x: x * 2).execute()
```

### Protocols for Flexibility

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> dict:
        ...

if isinstance(obj, Serializable):
    data = obj.to_dict()
```

---

## Integration Examples

### With FastAPI

```python
from fastapi import FastAPI
from python_mastery_portfolio import cache, DIContainer

app = FastAPI()
container = DIContainer()

@app.get("/users/{user_id}")
@cache(ttl=3600)
async def get_user(user_id: int):
    # Result cached for 1 hour
    return container.resolve(UserService).get(user_id)
```

### With Async Code

```python
import asyncio
from python_mastery_portfolio import async_retry, async_cache

@async_cache(maxsize=256)
async def fetch_data(url: str):
    # Cached async function
    return await http_client.get(url)

@async_retry(max_attempts=3, delay=0.5)
async def process_with_retry():
    # Retries on failure
    pass
```

---

## Performance Tips

1. **Use caching for pure functions**: Functions with no side effects cache perfectly
2. **Set appropriate TTL**: Balance between freshness and cache hits
3. **Monitor hit rates**: Use `cache_stats()` to see efficiency
4. **Use async for I/O**: Async versions prevent blocking
5. **DI for testability**: Makes mocking easier in tests

---

## Troubleshooting

### "Module not found" error
Make sure you've installed the package:
```bash
pip install -e ".[dev]"
```

### Type checking failures
Run mypy in strict mode:
```bash
mypy src/python_mastery_portfolio
```

### Tests failing
Make sure pytest-asyncio is installed:
```bash
pip install pytest-asyncio
```

---

## Resources

- **PATTERNS.md** - Comprehensive pattern guide
- **examples.py** - Real-world usage scenarios
- **test_advanced_features.py** - Test examples
- **Source code** - Fully commented and documented

---

## Next Steps

1. ✅ Explore the examples
2. ✅ Run the tests
3. ✅ Try using decorators in your code
4. ✅ Set up DI container for your services
5. ✅ Add caching to expensive functions

Your portfolio is now **production-ready** and demonstrates **expert-level Python skills**!

