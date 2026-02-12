# python-mastery-portfolio

![CI](https://github.com/exclipsee/python-mastery-portfolio/actions/workflows/ci.yml/badge.svg?branch=main) ![Codecov](https://codecov.io/gh/exclipsee/python-mastery-portfolio/branch/main/graph/badge.svg)

A comprehensive Python portfolio showcasing **advanced design patterns**, **production-grade code quality**, and **deep expertise** in modern Python development.

## Quick Highlights

✅ **79% Test Coverage** with comprehensive test suite  
✅ **Strict Type Hints** with mypy in strict mode  
✅ **Production-Grade Error Handling** with custom exception hierarchy  
✅ **Advanced Decorators** (retry, rate limiting, caching, validation)  
✅ **Dependency Injection Container** with lifecycle management  
✅ **Async/Await Support** with proper concurrency patterns  
✅ **Performance Optimization** with caching and lazy evaluation  
✅ **Real-world Patterns** demonstrating professional practices

## Core Features

### 1. Advanced Decorators & Patterns

```python
from python_mastery_portfolio import retry, async_retry, timed, cache

# Automatic retry with exponential backoff
@retry(max_attempts=3, delay=1.0, backoff=2.0)
def unstable_operation():
    pass

# Performance timing
@timed(unit='ms')
def compute():
    pass

# Function result caching
@cache(maxsize=256, ttl=3600)
def expensive_computation(x: int) -> int:
    return sum(range(x))
```

### 2. Custom Exception Hierarchy

```python
from python_mastery_portfolio import ValidationError, RateLimitError, ConfigurationError

try:
    if age < 0:
        raise ValidationError("Age cannot be negative", field="age", value=age)
except ValidationError as e:
    error_dict = e.to_dict()  # Convert to JSON
    print(e.context)          # Rich debugging info
```

### 3. Dependency Injection Container

```python
from python_mastery_portfolio import DIContainer, LifecycleScope

container = DIContainer()
container.register(DatabaseService, scope=LifecycleScope.SINGLETON)
container.register(RequestService, scope=LifecycleScope.TRANSIENT)

# Services auto-wire dependencies
db_service = container.resolve(DatabaseService)
```

### 4. Advanced Typing with Generics

```python
from python_mastery_portfolio import Container, Result, Pipeline

# Type-safe generic container
int_container: Container[int] = Container(42)
result = int_container.map(lambda x: x * 2)

# Result type for functional error handling
result: Result[int, str] = Result.success(42)
if result.is_success():
    print(result.get_or_raise())

# Fluent API for transformations
output = Pipeline(5).add(lambda x: x*2).add(lambda x: x+3).execute()
```

### 5. Production-Grade Caching

```python
from python_mastery_portfolio import LRUCache, async_cache

# Thread-safe LRU cache with TTL
cache: LRUCache[str, int] = LRUCache(maxsize=128, ttl=3600)
cache.set("key", 42)
value = cache.get("key")
stats = cache.stats()  # Hit rate, size, etc.

# Async support
@async_cache(maxsize=128)
async def fetch_data(user_id: int):
    return await api.get_user(user_id)
```

## Architecture

```
src/python_mastery_portfolio/
├── algorithms.py          # Core algorithms (fibonacci, binary search, gcd)
├── api.py                 # FastAPI with WebSockets, rate limiting
├── cli.py                 # CLI with Typer
├── ml_pipeline.py         # ML model training & prediction
├── doc_qa.py              # RAG question-answering system
├── embeddings.py          # Text embeddings
├── excel_tools.py         # Excel I/O utilities
├── system_metrics.py      # System monitoring
├── vin.py                 # VIN validation
├── websocket_manager.py   # WebSocket connection management
├── monitor.py             # URL monitoring
├── config.py              # Configuration management
├── logging_utils.py       # JSON logging setup
├── utils.py               # General utilities
│
# Advanced Patterns (NEW)
├── exceptions.py          # Custom exception hierarchy with context
├── decorators.py          # Retry, caching, timing, validation decorators
├── caching.py             # LRU cache with TTL support (sync & async)
├── di_container.py        # Dependency injection container
├── typing_utils.py        # Advanced typing (generics, protocols, result types)
└── examples.py            # Real-world usage examples
```

## Testing & Quality

```bash
# Run all tests with coverage
pytest                    # 79% coverage, 30+ test cases
pytest tests/test_advanced_features.py  # 31 tests for new patterns

# Type checking with strict mode
mypy src/

# Code formatting & linting
black src/
ruff check src/
```

## Key Concepts Demonstrated

### Design Patterns
- **Decorator Pattern**: Retry, caching, timing, validation
- **Factory Pattern**: Service registration and lifecycle management
- **Dependency Injection**: Container with automatic wiring
- **Observer Pattern**: WebSocket event broadcasting
- **Strategy Pattern**: Multiple implementations with swappable strategies

### Advanced Python Features
- **Generic Types**: Type-safe containers and pipelines
- **Protocols**: Structural subtyping for loose coupling
- **Descriptors**: Lazy-loaded cached properties
- **Context Managers**: Resource management and cleanup
- **ParamSpec & TypeVar**: Preserve function signatures in decorators
- **Async/Await**: Non-blocking I/O patterns

### Production Patterns
- **Error Context**: Rich debugging information with custom exceptions
- **Rate Limiting**: Token bucket algorithm for API protection
- **Caching Strategies**: LRU with TTL for performance
- **Dependency Injection**: Loose coupling for testability
- **Type Safety**: Strict mypy for compile-time checking

## Learning Resources

See **[PATTERNS.md](./PATTERNS.md)** for detailed explanations and examples of:
- Custom exception hierarchy
- Advanced decorators
- Caching patterns
- Dependency injection
- Advanced typing
- Performance optimization
- Production-grade error handling

## Installation & Usage

```bash
# Install package
pip install -e ".[dev]"

# Run CLI
pm-portfolio algorithms fibonacci 10

# Use as library
from python_mastery_portfolio import (
    fibonacci,
    retry,
    cache,
    DIContainer,
    ValidationError,
)
```

## What Makes This Portfolio Strong

1. **Production-Ready Code**
   - 79% test coverage
   - Strict type hints (mypy strict mode)
   - Comprehensive error handling
   - Clear logging & monitoring

2. **Advanced Python Knowledge**
   - Generic types and protocols
   - Decorators with proper function signatures
   - Async/await patterns
   - Descriptor protocol
   - Context managers

3. **Real-World Patterns**
   - Dependency injection
   - Rate limiting
   - Caching strategies
   - Error context propagation
   - Service lifecycle management

4. **Professional Practices**
   - CI/CD integration
   - Code quality tools
   - Consistent formatting
   - Clear documentation
   - Well-organized modules

## Examples

See `src/python_mastery_portfolio/examples.py` for real-world usage:

```python
# Data validation with error context
validator = DataValidator()
result = validator.validate_row(data)

# Cached database service
db = UserDatabase()
user = db.get_user(123)  # Cached for 1 hour

# Async processing with retry
processor = AsyncDataProcessor()
result = await processor.process_data_async(42)

# DI container usage
container = setup_di_container()
service = container.resolve(NotificationService)
```

---

**This portfolio demonstrates the kind of Python expertise employers look for**: clean code, advanced patterns, production-grade quality, and deep understanding of modern Python development practices.
