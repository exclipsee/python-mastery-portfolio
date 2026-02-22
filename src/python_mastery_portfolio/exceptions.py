"""Custom exception classes used across the package.

These exceptions carry an optional ``context`` mapping that can be serialized
for debugging and API responses via the ``to_dict`` helper.
"""

from __future__ import annotations

from typing import Any


class PortfolioError(Exception):
    """Base exception with optional structured context.

    Attributes:
        message: Human-readable message.
        error_code: Short machine-friendly error code.
        context: Optional additional contextual data.
    """

    def __init__(
        self, message: str, error_code: str | None = None, context: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation of the exception."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "exception_type": self.__class__.__name__,
        }



class ValidationError(PortfolioError):
    """Raised when an input validation failure occurs.

    The optional ``field`` and ``value`` are included in the ``context``.
    """

    def __init__(self, message: str, field: str | None = None, value: Any = None) -> None:
        context = {}
        if field:
            context["field"] = field
        if value is not None:
            context["value"] = value
        super().__init__(message, error_code="VALIDATION_ERROR", context=context)


class RateLimitError(PortfolioError):
    """Raised when a rate limit is exceeded.

    ``retry_after`` and ``limit`` (when provided) are included in the context.
    """

    def __init__(
        self, message: str, retry_after: float | None = None, limit: int | None = None
    ) -> None:
        context = {}
        if retry_after is not None:
            context["retry_after"] = retry_after
        if limit is not None:
            context["limit"] = limit
        super().__init__(message, error_code="RATE_LIMIT_EXCEEDED", context=context)


class ConfigurationError(PortfolioError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: str | None = None) -> None:
        context = {}
        if config_key:
            context["config_key"] = config_key
        super().__init__(message, error_code="CONFIG_ERROR", context=context)


class DataProcessingError(PortfolioError):
    """Raised when data processing steps fail (e.g. parsing or row errors)."""

    def __init__(self, message: str, step: str | None = None, row_index: int | None = None) -> None:
        context = {}
        if step:
            context["step"] = step
        if row_index is not None:
            context["row_index"] = row_index
        super().__init__(message, error_code="DATA_PROCESSING_ERROR", context=context)


class APIError(PortfolioError):
    """Generic API error wrapper.

    ``status_code`` and ``endpoint`` may be included in the context when known.
    """

    def __init__(
        self, message: str, status_code: int | None = None, endpoint: str | None = None
    ) -> None:
        context = {}
        if status_code is not None:
            context["status_code"] = status_code
        if endpoint:
            context["endpoint"] = endpoint
        super().__init__(message, error_code="API_ERROR", context=context)


