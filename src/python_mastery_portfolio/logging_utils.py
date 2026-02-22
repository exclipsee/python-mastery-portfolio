"""Small logging helpers used by the CLI and tests.

Provides a compact JSON formatter for structured logs and helpers to wire
logging configuration based on CLI flags or programmatic needs.
"""

from __future__ import annotations

import json
import logging


class JsonFormatter(logging.Formatter):
    """Formatter that serializes log records as JSON objects.

    The JSON payload contains timestamp, level, logger name and the rendered
    message. Exceptions (if present) are included under the ``exc`` key.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload = {"ts": self.formatTime(record), "level": record.levelname, "logger": record.name, "msg": record.getMessage()}
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging_from_cli(verbose: bool = False, json_output: bool = False) -> None:
    """Configure root logging for CLI use.

    Args:
        verbose: When true, set level to DEBUG, otherwise INFO.
        json_output: When true, use the :class:`JsonFormatter` to emit JSON logs.
    """
    level = logging.DEBUG if verbose else logging.INFO
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter() if json_output else logging.Formatter("%(asctime)s %(levelname)s - %(message)s"))
    root.handlers = [handler]


def setup_json_logging(level: int | None = None) -> None:
    """Programmatic shortcut to enable JSON logging on the root logger.

    Args:
        level: Optional numeric logging level to set on the root logger.
    """
    root = logging.getLogger()
    if level is not None:
        root.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.handlers = [handler]
