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

## Running locally

Start the API locally with Docker Compose:

```sh
docker-compose up --build
```

The service listens on port 8000 by default. A health probe is available at:

```
GET http://localhost:8000/health
```

The `/health` endpoint returns JSON with `status`, `uptime` (seconds), and `version`.


## Optional dependencies

Some features require optional extras. For embeddings/RAG functionality, install the `rag` extras:

```sh
pip install .[rag]
```

If `sentence-transformers` or `scikit-learn` are not installed, the library falls back to a deterministic, lightweight `SimpleEmbedder` implementation.
