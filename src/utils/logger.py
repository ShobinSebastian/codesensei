# src/utils/logger.py

"""
Structured Logging System
==========================
Production-grade logging with JSON formatting.

Features:
- JSON structured logs
- Context tracking
- Performance metrics
- Error tracking
- Request/response logging

Author: Shobin Sebastian
Date: December 2025
"""

import logging
import json
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import os


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Converts log records to JSON format with additional metadata.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        
        # Base log structure
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        # Add custom fields from record.__dict__
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName", "relativeCreated",
                "thread", "threadName", "exc_info", "exc_text", "stack_info"
            ]:
                try:
                    # Only add JSON-serializable values
                    json.dumps(value)
                    log_data[key] = value
                except (TypeError, ValueError):
                    log_data[key] = str(value)
        
        return json.dumps(log_data)


class ContextLogger:
    """
    Logger with context tracking.
    
    Automatically adds context information to all logs.
    """
    
    def __init__(self, name: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize context logger.
        
        Args:
            name: Logger name
            context: Additional context to include in all logs
        """
        self.logger = logging.getLogger(name)
        self.context = context or {}
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log message with context."""
        extra_fields = {**self.context, **kwargs}
        extra = {"extra_fields": extra_fields}
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        extra_fields = {**self.context, **kwargs}
        extra = {"extra_fields": extra_fields}
        self.logger.exception(message, extra=extra)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = True
) -> logging.Logger:
    """
    Set up application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        json_format: Use JSON formatting (True) or plain text (False)
    
    Returns:
        Configured root logger
    """
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if json_format:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
    
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        if json_format:
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            )
        
        root_logger.addHandler(file_handler)
    
    return root_logger


def get_logger(name: str, context: Optional[Dict[str, Any]] = None) -> ContextLogger:
    """
    Get a context logger instance.
    
    Args:
        name: Logger name (usually __name__)
        context: Optional context dictionary
    
    Returns:
        ContextLogger instance
    """
    return ContextLogger(name, context)


# Request/Response logging utilities
class RequestLogger:
    """Helper for logging API requests."""
    
    @staticmethod
    def log_request(logger: ContextLogger, request_id: str, method: str, 
                   path: str, client_ip: str):
        """Log incoming request."""
        logger.info(
            "Request received",
            request_id=request_id,
            method=method,
            path=path,
            client_ip=client_ip,
            event_type="request_start"
        )
    
    @staticmethod
    def log_response(logger: ContextLogger, request_id: str, status_code: int,
                    duration_ms: float, response_size: int):
        """Log request completion."""
        logger.info(
            "Request completed",
            request_id=request_id,
            status_code=status_code,
            duration_ms=duration_ms,
            response_size=response_size,
            event_type="request_complete"
        )
    
    @staticmethod
    def log_error(logger: ContextLogger, request_id: str, error: Exception,
                 status_code: int):
        """Log request error."""
        logger.error(
            f"Request failed: {str(error)}",
            request_id=request_id,
            error_type=type(error).__name__,
            status_code=status_code,
            event_type="request_error"
        )


# Example usage
if __name__ == "__main__":
    # Setup logging
    setup_logging(log_level="DEBUG", log_file="logs/app.log")
    
    # Create logger with context
    logger = get_logger(__name__, context={
        "service": "codesensei",
        "version": "0.3.0"
    })
    
    # Log examples
    logger.info("Application started", environment="production")
    logger.debug("Debug information", data={"key": "value"})
    logger.warning("Warning message", threshold_exceeded=True)
    
    try:
        # Simulate error
        raise ValueError("Example error")
    except Exception:
        logger.exception("An error occurred", user_id="12345")
    
    # Request logging
    request_logger = RequestLogger()
    request_logger.log_request(
        logger, 
        request_id="req-123",
        method="POST",
        path="/analyze",
        client_ip="192.168.1.1"
    )
    
    request_logger.log_response(
        logger,
        request_id="req-123",
        status_code=200,
        duration_ms=1250.5,
        response_size=2048
    )