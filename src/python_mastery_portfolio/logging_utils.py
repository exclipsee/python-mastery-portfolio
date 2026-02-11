from __future__ import annotations

import json
import logging


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {"ts": self.formatTime(record), "level": record.levelname, "logger": record.name, "msg": record.getMessage()}
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging_from_cli(verbose: bool = False, json_output: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter() if json_output else logging.Formatter("%(asctime)s %(levelname)s - %(message)s"))
    root.handlers = [handler]


def setup_json_logging(level: int | None = None) -> None:
    root = logging.getLogger()
    if level is not None:
        root.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.handlers = [handler]
