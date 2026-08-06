"""Enterprise Centralized Structured JSON Logging Engine."""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src.common.config.settings import get_settings


class StructuredJSONFormatter(logging.Formatter):
    """Formats log records as Google Cloud Logging compliant JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "correlation_id": getattr(record, "correlation_id", "N/A"),
            "execution_id": getattr(record, "execution_id", "N/A"),
            "batch_id": getattr(record, "batch_id", "N/A"),
            "trace_id": getattr(record, "trace_id", "N/A"),
            "error_category": getattr(record, "error_category", "NONE"),
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


class TelemetryLogger:
    """Enterprise Structured Logger providing correlation tracking and Google Cloud Logging compatibility."""

    def __init__(
        self,
        name: str = "platform_observability",
        correlation_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        batch_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ):
        self.settings = get_settings()
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, self.settings.log_level.upper(), logging.INFO))

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(StructuredJSONFormatter())
            self.logger.addHandler(handler)

        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.execution_id = execution_id or str(uuid.uuid4())
        self.batch_id = batch_id or "batch_default"
        self.trace_id = trace_id or str(uuid.uuid4())

    def _get_extra(self, error_category: str = "NONE") -> Dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "execution_id": self.execution_id,
            "batch_id": self.batch_id,
            "trace_id": self.trace_id,
            "error_category": error_category,
        }

    def info(self, msg: str) -> None:
        self.logger.info(msg, extra=self._get_extra())

    def warning(self, msg: str, error_category: str = "NONE") -> None:
        self.logger.warning(msg, extra=self._get_extra(error_category=error_category))

    def error(self, msg: str, error_category: str = "GENERAL_ERROR") -> None:
        self.logger.error(msg, extra=self._get_extra(error_category=error_category))

    def critical(self, msg: str, error_category: str = "INFRASTRUCTURE_ERROR") -> None:
        self.logger.critical(msg, extra=self._get_extra(error_category=error_category))
