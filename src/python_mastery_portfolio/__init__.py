"""Python Mastery Portfolio package.

This package exposes a small, stable public surface for downstream
consumers (tests, demos, notebooks). Internals live in their modules and are
not exported by default.
"""

from importlib import metadata as _metadata

from .algorithms import binary_search, fibonacci
from .utils import timeit
from .vin import compute_check_digit, is_valid_vin
from .config import load_config
from .logging_utils import configure_logging_from_cli

try:
    __version__ = _metadata.version("python-mastery-portfolio")
except Exception:
    __version__ = "0.0.0"

__all__ = [
    "fibonacci",
    "binary_search",
    "timeit",
    "compute_check_digit",
    "is_valid_vin",
    "load_config",
    "configure_logging_from_cli",
    "__version__",
]
