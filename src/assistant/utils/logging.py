"""Logging configuration and setup for AI assistants."""

import logging
import logging.config
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import threading
import structlog
from structlog.stdlib import LoggerFactory


class AssistantLogger:
    """Enhanced logger with structured logging and multiple output formats."""
    
    def __init__(
        self,
        name: str = "assistant",
        level: str = "INFO",
        log_file: Optional[str] = None,
        json_enabled: bool = False,
        console_enabled: bool = True,
        max_file_size: str = "10MB",
        backup_count: int = 5,
        context_fields: Optional[List[str]] = None
    ):
        """Initialize assistant logger.
        
        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to log file (optional)
            json_enabled: Enable JSON log format
            console_enabled: Enable console logging
            max_file_size: Maximum log file size
            backup_count: Number of backup files to keep
            context_fields: List of context fields to include in logs
        """
        self.name = name
        self.level = level.upper()
        self.log_file = log_file
        self.json_enabled = json_enabled
        self.console_enabled = console_enabled
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.context_fields = context_fields or []
        
        # Thread-safe context storage
        self._context = {}
        self._context_lock = threading.Lock()
        
        # Setup logging
        self._setup_logging()
        self._setup_structlog()
        
        # Get logger instance
        self.logger = structlog.get_logger(name)
    
    def _setup_logging(self) -> None:
        """Setup Python logging configuration."""
        config = self._get_logging_config()
        logging.config.dictConfig(config)
    
    def _get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration dictionary."""
        formatters = {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(module)s %(lineno)d %(message)s"
            }
        }
        
        handlers = {}
        
        # Console handler
        if self.console_enabled:
            handlers["console"] = {
                "class": "logging.StreamHandler",
                "level": self.level,
                "formatter": "detailed",
                "stream": "ext://sys.stdout"
            }
        
        # File handler with rotation
        if self.log_file:
            # Ensure log directory exists
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            handlers["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "level": self.level,
                "formatter": "json" if self.json_enabled else "detailed",
                "filename": self.log_file,
                "maxBytes": self._parse_size(self.max_file_size),
                "backupCount": self.backup_count,
                "encoding": "utf-8"
            }
            
            # Optional: separate JSON file handler
            if self.json_enabled and self.log_file:
                json_file = str(Path(self.log_file).with_suffix('.json'))
                handlers["json_file"] = {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": self.level,
                    "formatter": "json",
                    "filename": json_file,
                    "maxBytes": self._parse_size(self.max_file_size),
                    "backupCount": self.backup_count,
                    "encoding": "utf-8"
                }
        
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": formatters,
            "handlers": handlers,
            "loggers": {
                "": {
                    "level": self.level,
                    "handlers": list(handlers.keys()),
                    "propagate": False
                },
                "assistant": {
                    "level": self.level,
                    "handlers": list(handlers.keys()),
                    "propagate": False
                }
            }
        }
    
    def _setup_structlog(self) -> None:
        """Setup structlog configuration."""
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            self._add_context_info,
        ]
        
        if self.json_enabled:
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())
        
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    
    def _add_context_info(self, logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Add context information to log events."""
        with self._context_lock:
            context_copy = self._context.copy()
        
        event_dict.update(context_copy)
        return event_dict
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string to bytes."""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def set_context(self, **kwargs) -> None:
        """Set context information for all future logs."""
        with self._context_lock:
            self._context.update(kwargs)
    
    def clear_context(self) -> None:
        """Clear all context information."""
        with self._context_lock:
            self._context.clear()
    
    def bind(self, **kwargs) -> "AssistantLogger":
        """Create a new logger instance with additional context."""
        new_logger = AssistantLogger(
            name=self.name,
            level=self.level,
            log_file=self.log_file,
            json_enabled=self.json_enabled,
            console_enabled=self.console_enabled,
            max_file_size=self.max_file_size,
            backup_count=self.backup_count,
            context_fields=self.context_fields
        )
        
        # Copy existing context
        with self._context_lock:
            new_logger._context = self._context.copy()
        
        # Add new context
        new_logger.set_context(**kwargs)
        return new_logger
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        self.logger.exception(message, **kwargs)
    
    def log_function_call(self, func_name: str, args: tuple = (), kwargs: dict = None, **log_kwargs) -> None:
        """Log function call with parameters."""
        kwargs = kwargs or {}
        self.info(
            "Function called",
            function=func_name,
            args_count=len(args),
            kwargs_keys=list(kwargs.keys()),
            **log_kwargs
        )
    
    def log_function_result(self, func_name: str, result: Any, execution_time: Optional[float] = None, **log_kwargs) -> None:
        """Log function execution result."""
        result_info = {
            "function": func_name,
            "result_type": type(result).__name__,
            "result_size": len(str(result)) if isinstance(result, (str, list, dict)) else None,
        }
        
        if execution_time is not None:
            result_info["execution_time_ms"] = round(execution_time * 1000, 2)
        
        result_info.update(log_kwargs)
        
        if execution_time and execution_time > 1.0:  # Only warn for slow functions
            self.warning("Function completed slowly", **result_info)
        else:
            self.info("Function completed", **result_info)
    
    def log_request(self, method: str, path: str, user_id: Optional[str] = None, **kwargs) -> None:
        """Log API request."""
        self.info(
            "API request",
            method=method,
            path=path,
            user_id=user_id,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
    
    def log_response(
        self,
        method: str,
        path: str,
        status_code: int,
        response_time_ms: float,
        user_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log API response."""
        log_level = "error" if status_code >= 400 else "debug" if status_code < 300 else "info"
        
        getattr(self, log_level)(
            "API response",
            method=method,
            path=path,
            status_code=status_code,
            response_time_ms=round(response_time_ms, 2),
            user_id=user_id,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
    
    def log_security_event(self, event_type: str, user_id: Optional[str] = None, **kwargs) -> None:
        """Log security-related events."""
        self.warning(
            "Security event",
            event_type=event_type,
            user_id=user_id,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
    
    def log_performance(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        **kwargs
    ) -> None:
        """Log performance metrics."""
        log_level = "info" if success and duration_ms < 1000 else "warning"
        
        getattr(self, log_level)(
            "Performance metric",
            operation=operation,
            duration_ms=round(duration_ms, 2),
            success=success,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )


class LoggerManager:
    """Manages multiple logger instances."""
    
    def __init__(self):
        """Initialize logger manager."""
        self._loggers: Dict[str, AssistantLogger] = {}
        self._config: Dict[str, Any] = {}
    
    def get_logger(
        self,
        name: str,
        level: Optional[str] = None,
        log_file: Optional[str] = None,
        **kwargs
    ) -> AssistantLogger:
        """Get or create logger instance."""
        if name not in self._loggers:
            # Use global config defaults if not provided
            config = self._config.copy()
            config.update(kwargs)
            
            if level is None:
                level = config.get("level", "INFO")
            if log_file is None:
                log_file = config.get("log_file")
            
            self._loggers[name] = AssistantLogger(
                name=name,
                level=level,
                log_file=log_file,
                **config
            )
        
        return self._loggers[name]
    
    def configure_global(self, **config) -> None:
        """Configure global logging settings."""
        self._config.update(config)
    
    def shutdown(self) -> None:
        """Shutdown all loggers."""
        for logger in self._loggers.values():
            # Clear any pending log handlers
            handlers = logger.logger.logger.handlers.copy()
            for handler in handlers:
                handler.close()
                logger.logger.logger.removeHandler(handler)
        
        self._loggers.clear()


# Global logger manager instance
logger_manager = LoggerManager()


def get_logger(name: str = "assistant", **kwargs) -> AssistantLogger:
    """Get logger instance using global manager."""
    return logger_manager.get_logger(name, **kwargs)


def configure_logging(**config) -> None:
    """Configure global logging settings."""
    logger_manager.configure_global(**config)