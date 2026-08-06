"""Enterprise structured logging framework.

Provides environment-aware JSON logging for cloud compatibility (Cloud Logging)
and human-readable console logging for local development, with correlation ID support.
"""

import contextvars
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict

# Context variable for tracking correlation IDs across execution contexts
_CORRELATION_ID: contextvars.ContextVar[str] = contextvars.ContextVar("correlation_id", default="N/A")


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current thread/async context.

    Args:
        correlation_id: Unique correlation identifier for tracing.
    """
    _CORRELATION_ID.set(correlation_id)


class JSONFormatter(logging.Formatter):
    """JSON log formatter for production and cloud logging environments."""

    def format(self, record: logging.LogRecord) -> str:
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": _CORRELATION_ID.get(),
            "environment": os.getenv("ENVIRONMENT", "dev"),
            "location": f"{record.module}.py:{record.lineno}",
        }

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_payload.update(record.extra)

        return json.dumps(log_payload)


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "correlation_id"):
            record.correlation_id = _CORRELATION_ID.get()
        return True


def get_logger(name: str) -> logging.Logger:
    """Instantiate and configure an environment-aware structured logger.

    Args:
        name: Name of the module requesting logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(ContextFilter())
    env = os.getenv("ENVIRONMENT", "dev").lower()

    if env == "prod":
        handler.setFormatter(JSONFormatter())
    else:
        fmt = "[%(asctime)s] [%(levelname)s] [%(name)s] [CorrID: %(correlation_id)s]: %(message)s"
        handler.setFormatter(logging.Formatter(fmt))

    logger.addHandler(handler)
    logger.propagate = False
    return logger
