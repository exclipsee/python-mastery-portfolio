"""Custom exception classes and error handling utilities."""

from __future__ import annotations

import logging
import sys
import traceback
from typing import Any

logger = logging.getLogger("exceptions")


class PortfolioError(Exception):
    """Base exception for all portfolio-related errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize PortfolioError with context.

        Args:
            message: Human-readable error message
            error_code: Unique error code for programmatic handling
            context: Additional context data for debugging
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self._log_error()

    def _log_error(self) -> None:
        """Log error with full context."""
        logger.error(
            f"{self.error_code}: {self.message}",
            extra={"context": self.context, "exception": self.__class__.__name__},
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary representation."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "exception_type": self.__class__.__name__,
        }

    def __repr__(self) -> str:
        """Return detailed representation."""
        return (
            f"{self.__class__.__name__}"
            f"(message={self.message!r}, error_code={self.error_code!r})"
        )


class ValidationError(PortfolioError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any = None,
    ) -> None:
        """
        Initialize ValidationError.

        Args:
            message: Error message
            field: Field that failed validation
            value: The invalid value
        """
        context = {}
        if field:
            context["field"] = field
        if value is not None:
            context["value"] = value
        super().__init__(message, error_code="VALIDATION_ERROR", context=context)


class RateLimitError(PortfolioError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        retry_after: float | None = None,
        limit: int | None = None,
    ) -> None:
        """
        Initialize RateLimitError.

        Args:
            message: Error message
            retry_after: Seconds to wait before retry
            limit: Rate limit threshold
        """
        context = {}
        if retry_after is not None:
            context["retry_after"] = retry_after
        if limit is not None:
            context["limit"] = limit
        super().__init__(message, error_code="RATE_LIMIT_EXCEEDED", context=context)


class ConfigurationError(PortfolioError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, config_key: str | None = None) -> None:
        """
        Initialize ConfigurationError.

        Args:
            message: Error message
            config_key: Configuration key that failed
        """
        context = {}
        if config_key:
            context["config_key"] = config_key
        super().__init__(message, error_code="CONFIG_ERROR", context=context)


class DataProcessingError(PortfolioError):
    """Raised when data processing fails."""

    def __init__(
        self,
        message: str,
        step: str | None = None,
        row_index: int | None = None,
    ) -> None:
        """
        Initialize DataProcessingError.

        Args:
            message: Error message
            step: Processing step where error occurred
            row_index: Index of problematic row in batch
        """
        context = {}
        if step:
            context["step"] = step
        if row_index is not None:
            context["row_index"] = row_index
        super().__init__(message, error_code="DATA_PROCESSING_ERROR", context=context)


class APIError(PortfolioError):
    """Raised for API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        endpoint: str | None = None,
    ) -> None:
        """
        Initialize APIError.

        Args:
            message: Error message
            status_code: HTTP status code
            endpoint: API endpoint that failed
        """
        context = {}
        if status_code is not None:
            context["status_code"] = status_code
        if endpoint:
            context["endpoint"] = endpoint
        super().__init__(message, error_code="API_ERROR", context=context)


def format_exception_with_context() -> str:
    """Format current exception with full traceback and context."""
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if exc_type is None:
        return "No active exception"

    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    formatted = "".join(tb_lines)

    if isinstance(exc_value, PortfolioError):
        formatted += f"\nContext: {exc_value.context}"

    return formatted


def handle_exception(exc: Exception, reraise: bool = True) -> dict[str, Any]:
    """
    Handle exception and optionally reraise.

    Args:
        exc: Exception to handle
        reraise: Whether to reraise after handling

    Returns:
        Dictionary with error information

    Raises:
        Exception: If reraise is True
    """
    error_dict = {
        "exception_type": exc.__class__.__name__,
        "message": str(exc),
    }

    if isinstance(exc, PortfolioError):
        error_dict.update(exc.to_dict())

    logger.error(f"Exception handled: {error_dict}")

    if reraise:
        raise

    return error_dict

