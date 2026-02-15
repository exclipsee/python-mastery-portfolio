"""Public package exports."""

from importlib import metadata as _metadata

from .algorithms import binary_search, fibonacci
from .caching import LRUCache, async_cache, cache
from .decorators import CachedProperty, async_retry, retry, timed, validate_types
from .di_container import DIContainer, LifecycleScope, get_container
from .exceptions import (
    APIError,
    ConfigurationError,
    DataProcessingError,
    PortfolioError,
    RateLimitError,
    ValidationError,
)
from .typing_utils import Container, Pipeline, Result
from .utils import timeit
from .vin import compute_check_digit, is_valid_vin

try:
    __version__ = _metadata.version("python-mastery-portfolio")
except Exception:
    __version__ = "0.0.0"

__all__ = [
    # Core patterns
    "retry", "async_retry", "timed", "validate_types", "CachedProperty",
    "LRUCache", "cache", "async_cache",
    "DIContainer", "LifecycleScope", "get_container",
    "PortfolioError", "ValidationError", "RateLimitError", "ConfigurationError", "DataProcessingError", "APIError",
    "Container", "Pipeline", "Result",
    # Classic modules
    "fibonacci", "binary_search", "timeit", "compute_check_digit", "is_valid_vin",
    "__version__",
]
