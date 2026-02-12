# Advanced Python Patterns & Design Patterns

This document showcases advanced Python patterns and techniques used throughout the portfolio to demonstrate deep expertise.

## 1. Custom Exception Hierarchy (`exceptions.py`)

**Pattern**: Structured Error Handling with Context

Custom exceptions provide rich error information and context for better debugging:

```python
from python_mastery_portfolio import (
    PortfolioError,
    ValidationError,
    RateLimitError,
    ConfigurationError,
    DataProcessingError,
    APIError,
)

# Raises ValidationError with field and value context
try:
    if user_age < 0:
        raise ValidationError("Age cannot be negative", field="age", value=user_age)
except ValidationError as e:
    print(e.to_dict())  # Convert to dict for JSON serialization
    print(e.context)    # Access additional context
```

**Why it matters**:
- Structured error handling enables better logging and monitoring
- Type hints on exceptions make error handling explicit
- Context dictionary allows rich debugging information
- Production-grade error reporting capabilities

---

## 2. Advanced Decorators (`decorators.py`)

### 2.1 Retry with Exponential Backoff

```python
from python_mastery_portfolio import retry, async_retry

@retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=(IOError, ConnectionError))
def unstable_operation():
    # Automatically retries 3 times with increasing delay
    pass

@async_retry(max_attempts=5, delay=0.5)
async def async_unstable_operation():
    # Same pattern for async functions
    pass
```

**Pattern**: Decorators with ParamSpec & TypeVar
- Uses `ParamSpec` for type-safe parameter passing
- `TypeVar` for return type preservation
- Works with both sync and async functions

### 2.2 Performance Timing Decorator

```python
from python_mastery_portfolio import timed

@timed(unit='ms')
def slow_function():
    # Automatically logs execution time in milliseconds
    pass
```

### 2.3 Runtime Type Validation

```python
from python_mastery_portfolio import validate_types

@validate_types(name=str, age=int, email=str)
def create_user(name: str, age: int, email: str):
    # Validates argument types at runtime, raises ValidationError if invalid
    pass
```

### 2.4 Cached Property Descriptor

```python
from python_mastery_portfolio import CachedProperty

class ExpensiveComputation:
    @CachedProperty
    def result(self):
        # Computed only once, then cached
        return sum(range(1000000))
```

**Pattern**: Descriptors for Lazy Evaluation
- Implements `__get__` protocol
- Caches result after first access
- Generic typing with `Generic[T]`

---

## 3. Advanced Typing (`typing_utils.py`)

### 3.1 Generic Container

```python
from python_mastery_portfolio import Container

# Type-safe generic container
int_container: Container[int] = Container(42)
str_container: Container[str] = Container("hello")

# Map operation with type preservation
result = int_container.map(lambda x: x * 2)  # Still Container[int]
```

### 3.2 Result Type (Option/Either Pattern)

```python
from python_mastery_portfolio import Result

def divide(a: int, b: int) -> Result[float, str]:
    if b == 0:
        return Result.failure("Cannot divide by zero")
    return Result.success(a / b)

# Functional error handling
result = divide(10, 2)
if result.is_success():
    print(result.get_or_raise())
else:
    print(f"Error: {result.error}")
```

### 3.3 Pipeline for Transformations

```python
from python_mastery_portfolio import Pipeline

# Fluent API for chaining transformations
result = Pipeline(5)\
    .add(lambda x: x * 2)\
    .add(lambda x: x + 3)\
    .add(lambda x: x ** 2)\
    .execute()  # Returns 169
```

### 3.4 Protocols for Structural Typing

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serializable(Protocol):
    """Protocol for serializable objects."""
    def to_dict(self) -> dict:
        ...

# Any class implementing to_dict() satisfies this protocol
if isinstance(my_object, Serializable):
    data = my_object.to_dict()
```

**Pattern**: Structural Subtyping
- Protocols define interfaces without inheritance
- `@runtime_checkable` enables isinstance checks
- More Pythonic than abstract base classes in many cases

---

## 4. Caching Patterns (`caching.py`)

### 4.1 LRU Cache with TTL

```python
from python_mastery_portfolio import LRUCache, cache

# Manual cache management
cache_store: LRUCache[str, int] = LRUCache(maxsize=128, ttl=3600)
cache_store.set("user:123", 42)
value = cache_store.get("user:123")

# Get statistics
stats = cache_store.stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")  # Shows cache efficiency
```

### 4.2 Decorator-based Caching

```python
from python_mastery_portfolio import cache, async_cache

@cache(maxsize=256, ttl=3600)
def expensive_computation(x: int) -> int:
    # Results cached for 1 hour
    return sum(range(x))

# Access cache stats
print(expensive_computation.cache_stats())
expensive_computation.cache_clear()  # Manual invalidation

@async_cache(maxsize=128)
async def async_expensive_operation(user_id: int):
    # Works with async functions too
    return await fetch_user_data(user_id)
```

**Pattern**: Thread-safe & Async-safe Caching
- Uses `threading.Lock` for sync, `asyncio.Lock` for async
- Automatic TTL expiration
- Entry access tracking
- LRU eviction policy

---

## 5. Dependency Injection Container (`di_container.py`)

### 5.1 Service Registration & Resolution

```python
from python_mastery_portfolio import DIContainer, LifecycleScope

container = DIContainer()

# Register services with different lifecycles
container.register(DatabaseService, scope=LifecycleScope.SINGLETON)
container.register(RequestService, scope=LifecycleScope.TRANSIENT)

# Resolve services
db = container.resolve(DatabaseService)  # Same instance every time
req = container.resolve(RequestService)  # New instance each time
```

### 5.2 Factory Functions

```python
def database_factory() -> DatabaseService:
    return DatabaseService(connection_string="postgresql://...")

container.register(DatabaseService, factory=database_factory)

# Factory receives dependencies automatically
def config_aware_factory(config: Config) -> Service:
    return Service(config)

container.register(Service, factory=config_aware_factory)
```

### 5.3 Service Provider Decorator

```python
from python_mastery_portfolio import ServiceProvider

provider = ServiceProvider(container)

@provider.inject(DatabaseService)
def process_data(db: DatabaseService):
    # db is automatically injected
    return db.query()
```

**Pattern**: Inversion of Control (IoC)
- Lifecycle management (Singleton, Transient, Scoped)
- Automatic dependency resolution via inspection
- Decorator-based injection
- Supports chaining for fluent registration

---

## 6. Testing Patterns

### 6.1 Comprehensive Test Coverage

The test suite demonstrates advanced testing techniques:

```python
# tests/test_advanced_features.py
```

- **Parametrized Tests**: Multiple test cases with different inputs
- **Fixtures**: Reusable test setup with different scopes
- **Mocking**: Using monkeypatch for side effects
- **Async Tests**: Full support for async function testing
- **Exception Testing**: Verifying error handling

### 6.2 Example Test Structure

```python
import pytest

class TestDecorators:
    def test_retry_success(self):
        """Test retry decorator succeeds on first try."""
        # ...

    def test_retry_with_backoff(self):
        """Test exponential backoff behavior."""
        # ...

    @pytest.mark.asyncio
    async def test_async_retry(self):
        """Test async retry functionality."""
        # ...
```

**Best Practices Demonstrated**:
- Clear test naming (test_<feature>_<scenario>)
- Docstrings explaining intent
- Class-based organization for related tests
- Async test support with pytest-asyncio

---

## 7. Advanced Type Hints

### 7.1 Generic Types

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Repository(Generic[T]):
    def save(self, item: T) -> None:
        ...

    def get(self) -> T | None:
        ...

# Type-safe usage
repo: Repository[User] = Repository()
user = repo.get()  # Type checker knows this is User | None
```

### 7.2 Union & Literal Types

```python
from typing import Union, Literal

Status = Literal["pending", "active", "deleted"]

def update_status(user_id: int, status: Status) -> None:
    # Type checker ensures status is one of the allowed values
    pass
```

### 7.3 Callable Protocols

```python
from typing import Callable

def apply_transform(
    data: list[int],
    transform: Callable[[int], int]
) -> list[int]:
    # Transform must be a function taking int, returning int
    return [transform(x) for x in data]
```

---

## 8. Performance Optimization

### 8.1 Context Managers

```python
from python_mastery_portfolio import measure_block

with measure_block("data_processing"):
    # Code block is timed and logged
    process_large_dataset()
```

### 8.2 CachedProperty for Expensive Attributes

```python
class DataProcessor:
    @CachedProperty
    def model(self):
        # Loaded only once, reused thereafter
        return load_large_ml_model()
```

### 8.3 Async Patterns for Concurrency

The WebSocket and async caching examples show:
- `asyncio.Lock` for thread-safe async operations
- Async context managers
- Proper cancellation handling

---

## 9. Production-Grade Patterns

### 9.1 Error Context & Logging

```python
from python_mastery_portfolio import DataProcessingError

try:
    process_row(data, index=42)
except Exception as e:
    raise DataProcessingError(
        "Failed to process row",
        step="validation",
        row_index=42
    ) from e
```

### 9.2 Rate Limiting

```python
from python_mastery_portfolio import RateLimitError

def check_rate_limit(user_id: str) -> None:
    if user_requests[user_id] > LIMIT:
        raise RateLimitError(
            "Too many requests",
            retry_after=60.0,
            limit=LIMIT
        )
```

### 9.3 Configuration Management

```python
from python_mastery_portfolio import ConfigurationError

try:
    api_key = os.environ["API_KEY"]
except KeyError:
    raise ConfigurationError(
        "Missing required environment variable",
        config_key="API_KEY"
    )
```

---

## Key Takeaways

This portfolio demonstrates mastery of:

1. **Type Safety**: Strict mypy configuration with advanced typing patterns
2. **Error Handling**: Custom exceptions with rich context
3. **Design Patterns**: Decorators, factories, DI, protocols
4. **Async Programming**: Both async decorators and context managers
5. **Performance**: Caching, lazy evaluation, optimization techniques
6. **Testing**: Comprehensive test coverage with advanced patterns
7. **Code Quality**: 80%+ test coverage, black/ruff formatting, production-grade practices

All code follows PEP 8, uses type hints extensively, and demonstrates real-world production patterns.

