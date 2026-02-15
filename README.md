# python-mastery-portfolio

![CI](https://github.com/exclipsee/python-mastery-portfolio/actions/workflows/ci.yml/badge.svg?branch=main) ![Codecov](https://codecov.io/gh/exclipsee/python-mastery-portfolio/branch/main/graph/badge.svg)

Production-grade Python: decorators, caching, DI, exceptions, typing.

## Features

- **Decorators**: `@retry`, `@async_retry`, `@timed`, `@validate_types`
- **Caching**: `@cache`, `@async_cache`, LRUCache (thread-safe + async-safe)
- **Error Handling**: Custom exceptions with rich context
- **DI Container**: Singleton/Transient/Scoped lifecycle management
- **Advanced Typing**: Result[T,U], Container[T], Pipeline[T], Protocols

## Modules

| Module | What |
|--------|------|
| exceptions.py | Custom exception hierarchy |
| decorators.py | @retry, @cache, @timed, @validate_types |
| caching.py | LRU cache (sync & async) |
| di_container.py | Dependency injection |
| typing_utils.py | Result, Container, Pipeline |

