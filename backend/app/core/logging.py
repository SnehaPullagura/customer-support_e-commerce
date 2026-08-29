"""
Structured logging configuration and correlation context.
"""

import contextvars
import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from app.core.config import settings

# Context variable for request tracing / correlation ID
correlation_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default=""
)


def get_correlation_id() -> str:
    cid = correlation_id_ctx.get()
    if not cid:
        cid = str(uuid.uuid4())
        correlation_id_ctx.set(cid)
    return cid


def set_correlation_id(cid: str) -> None:
    correlation_id_ctx.set(cid)


class JSONFormatter(logging.Formatter):
    """Formats log records into machine-readable structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id_ctx.get() or None,
            "module": record.module,
            "line": record.lineno,
        }

        if hasattr(record, "props") and isinstance(record.props, dict):
            log_obj["props"] = record.props

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def setup_logging() -> None:
    """Configures root and application loggers."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    if settings.ENVIRONMENT == "production":
        stream_handler.setFormatter(JSONFormatter())
    else:
        color_formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s] [cid=%(correlation_id)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        stream_handler.setFormatter(color_formatter)

    root_logger.addHandler(stream_handler)
