"""Public package exports."""

from importlib import metadata as _metadata

from .algorithms import binary_search, fibonacci
from .caching import LRUCache, async_cache, cache
from .config import load_config
from .decorators import CachedProperty, async_retry, retry, timed, validate_types
from .di_container import DIContainer, LifecycleScope, ServiceProvider, get_container
from .exceptions import (
    APIError,
    ConfigurationError,
    DataProcessingError,
    PortfolioError,
    RateLimitError,
    ValidationError,
)
from .logging_utils import configure_logging_from_cli
from .typing_utils import Container, Pipeline, Result, TypedDict
from .utils import timeit
from .vin import compute_check_digit, is_valid_vin

try:
    __version__ = _metadata.version("python-mastery-portfolio")
except Exception:
    __version__ = "0.0.0"

__all__ = [
    # Algorithms
    "fibonacci",
    "binary_search",
    # Caching
    "LRUCache",
    "cache",
    "async_cache",
    # Decorators
    "retry",
    "async_retry",
    "timed",
    "validate_types",
    "CachedProperty",
    # DI Container
    "DIContainer",
    "LifecycleScope",
    "ServiceProvider",
    "get_container",
    # Exceptions
    "PortfolioError",
    "ValidationError",
    "RateLimitError",
    "ConfigurationError",
    "DataProcessingError",
    "APIError",
    # Typing
    "Container",
    "Pipeline",
    "Result",
    "TypedDict",
    # Utilities
    "timeit",
    "compute_check_digit",
    "is_valid_vin",
    "load_config",
    "configure_logging_from_cli",
    "__version__",
]
