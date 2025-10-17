"""Python Mastery Portfolio package.

This package collects small, well-crafted examples that demonstrate:
- Clean architecture and separation of concerns
- Strong typing and documentation
- Testability and performance awareness
"""

from .algorithms import binary_search, fibonacci
from .utils import timeit
from .vin import compute_check_digit, is_valid_vin, normalize_vin

__all__ = [
    "fibonacci",
    "binary_search",
    "timeit",
    "normalize_vin",
    "compute_check_digit",
    "is_valid_vin",
]
