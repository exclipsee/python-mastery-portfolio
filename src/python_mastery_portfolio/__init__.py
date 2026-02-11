"""Public package exports."""

from importlib import metadata as _metadata

from .algorithms import binary_search, fibonacci
from .config import load_config
from .logging_utils import configure_logging_from_cli
from .utils import timeit
from .vin import compute_check_digit, is_valid_vin

try:
    __version__ = _metadata.version("python-mastery-portfolio")
except Exception:
    __version__ = "0.0.0"

__all__ = ["fibonacci", "binary_search", "timeit", "compute_check_digit", "is_valid_vin", "load_config", "configure_logging_from_cli", "__version__"]
