"""Example usage of advanced patterns for real-world scenarios."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Generic, TypeVar

from .caching import async_cache, cache
from .decorators import async_retry, retry, timed, validate_types
from .di_container import DIContainer, LifecycleScope
from .exceptions import DataProcessingError, ValidationError
from .typing_utils import Result

T = TypeVar("T")


# Example 1: Data Pipeline with Error Handling & Validation


@dataclass
class DataRow:
    """Represents a single row of data."""

    id: int
    value: str
    score: float


class DataValidator:
    """Validates data with rich error context."""

    @validate_types(row=DataRow)
    def validate_row(self, row: DataRow) -> Result[DataRow, str]:
        """Validate a single data row."""
        try:
            if not row.value or len(row.value) > 100:
                raise ValidationError(
                    "Value must be 1-100 characters",
                    field="value",
                    value=row.value,
                )
            if row.score < 0 or row.score > 100:
                raise ValidationError(
                    "Score must be 0-100",
                    field="score",
                    value=row.score,
                )
            return Result.success(row)
        except ValidationError as e:
            return Result.failure(e.message)


# Example 2: Cached Data Service


class UserDatabase:
    """Simulated database with caching."""

    @cache(maxsize=256, ttl=3600)
    def get_user(self, user_id: int) -> dict[str, str]:
        """Get user data with automatic caching."""
        # Simulate expensive database query
        return {
            "id": str(user_id),
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com",
        }

    @retry(max_attempts=3, delay=0.5, exceptions=(ConnectionError,))
    def get_user_transactions(self, user_id: int) -> list[dict[str, str]]:
        """Get user transactions with retry logic."""
        # Simulate API call that might fail
        return [
            {"amount": "100", "date": "2024-01-01"},
            {"amount": "200", "date": "2024-01-02"},
        ]


# Example 3: Async Processing Pipeline


class AsyncDataProcessor:
    """Async processing with caching and retry logic."""

    @async_cache(maxsize=128)
    async def process_data_async(self, data_id: int) -> dict[str, str]:
        """Process data asynchronously with caching."""
        await asyncio.sleep(0.1)  # Simulate async work
        return {"id": str(data_id), "processed": "true"}

    @async_retry(max_attempts=3, delay=0.1, exceptions=(TimeoutError,))
    async def fetch_from_api(self, endpoint: str) -> dict[str, str]:
        """Fetch from API with retry on timeout."""
        await asyncio.sleep(0.05)
        return {"endpoint": endpoint, "status": "ok"}


# Example 4: DI Container for Service Management


class EmailService:
    """Sends emails."""

    def send(self, to: str, subject: str) -> None:
        """Send email."""
        print(f"Email sent to {to}: {subject}")


class NotificationService:
    """Depends on EmailService."""

    def __init__(self, email_service: EmailService) -> None:
        """Initialize with email service."""
        self.email_service = email_service

    def notify_user(self, user_id: int) -> None:
        """Notify user via email."""
        self.email_service.send(f"user{user_id}@example.com", "Notification")


def setup_di_container() -> DIContainer:
    """Set up DI container for services."""
    container = DIContainer()

    # Register services with appropriate lifetimes
    container.register(EmailService, scope=LifecycleScope.SINGLETON)
    container.register(NotificationService, scope=LifecycleScope.SINGLETON)

    return container


# Example 5: Performance Optimization with Decorators


class ComputeService:
    """Service with performance-critical operations."""

    @timed(unit="ms")
    def fast_computation(self, n: int) -> int:
        """Fast computation that's timed."""
        return sum(range(n))

    @cache(maxsize=128)
    @timed(unit="ms")
    def expensive_computation(self, n: int) -> int:
        """Expensive computation that's cached and timed."""
        return sum(i ** 2 for i in range(n))


# Example 6: Complex Data Transformation


class DataTransformer:
    """Transforms data with error handling."""

    def transform_batch(self, rows: list[DataRow]) -> Result[list[DataRow], str]:
        """Transform a batch of rows."""
        try:
            validator = DataValidator()
            transformed = []

            for i, row in enumerate(rows):
                result = validator.validate_row(row)
                if result.is_failure():
                    raise DataProcessingError(
                        result.error, step="validation", row_index=i
                    )
                transformed.append(result.get_or_raise())

            return Result.success(transformed)

        except DataProcessingError as e:
            return Result.failure(f"Batch processing failed: {e.message}")


# Example 7: Async Worker with Retry


class AsyncWorker:
    """Processes tasks asynchronously with retry."""

    @async_retry(max_attempts=5, delay=0.5)
    async def process_task(self, task_id: int) -> str:
        """Process a task with automatic retry."""
        await asyncio.sleep(0.1)
        return f"Task {task_id} processed"

    async def process_batch(self, task_ids: list[int]) -> list[str]:
        """Process multiple tasks concurrently."""
        results = await asyncio.gather(
            *[self.process_task(tid) for tid in task_ids]
        )
        return results


# Example Usage Functions


def example_validation_and_caching() -> None:
    """Example: Data validation with caching."""
    validator = DataValidator()
    db = UserDatabase()

    # Validate a row
    row = DataRow(id=1, value="Test", score=85.5)
    result = validator.validate_row(row)
    assert result.is_success()

    # Use cached database
    user1 = db.get_user(1)
    user1_cached = db.get_user(1)  # From cache

    print("Validation and caching example completed successfully")


async def example_async_processing() -> None:
    """Example: Async processing with retry."""
    processor = AsyncDataProcessor()

    # Process data
    result = await processor.process_data_async(1)
    print(f"Processed: {result}")

    # Fetch from API with retry
    api_result = await processor.fetch_from_api("/users")
    print(f"API Result: {api_result}")


def example_di_container() -> None:
    """Example: DI container usage."""
    container = setup_di_container()

    # Resolve services
    notification_service = container.resolve(NotificationService)
    notification_service.notify_user(123)

    print("DI container example completed successfully")


def example_error_handling() -> None:
    """Example: Error handling with context."""
    transformer = DataTransformer()

    # Valid data
    rows = [
        DataRow(id=1, value="Valid", score=50.0),
        DataRow(id=2, value="Also Valid", score=75.0),
    ]
    result = transformer.transform_batch(rows)
    assert result.is_success()

    # Invalid data
    invalid_rows = [DataRow(id=1, value="x" * 101, score=85.0)]
    result = transformer.transform_batch(invalid_rows)
    assert result.is_failure()

    print("Error handling example completed successfully")


if __name__ == "__main__":
    # Run synchronous examples
    example_validation_and_caching()
    example_di_container()
    example_error_handling()

    # Run async examples
    asyncio.run(example_async_processing())

    print("\nAll examples completed!")

