"""Structured logging utilities with context management."""

import threading
import uuid
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager
from functools import wraps

from .logging import AssistantLogger


@dataclass
class LogContext:
    """Structured logging context data."""
    
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    component: Optional[str] = None
    operation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        data = asdict(self)
        # Filter out None values
        return {k: v for k, v in data.items() if v is not None or v == []}


class StructuredLogger:
    """Enhanced logger with structured context management."""
    
    def __init__(self, base_logger: AssistantLogger):
        """Initialize structured logger.
        
        Args:
            base_logger: Base assistant logger
        """
        self.base_logger = base_logger
        self._context_stack: List[LogContext] = []
        self._context_lock = threading.Lock()
        
        # Global context that persists across all operations
        self._global_context = LogContext()
    
    def set_global_context(self, **kwargs) -> None:
        """Set global context values."""
        for key, value in kwargs.items():
            if hasattr(self._global_context, key):
                setattr(self._global_context, key, value)
            else:
                self._global_context.metadata[key] = value
    
    def clear_global_context(self) -> None:
        """Clear global context."""
        self._global_context = LogContext()
    
    @contextmanager
    def context(self, **kwargs):
        """Context manager for temporary logging context.
        
        Args:
            **kwargs: Context values to apply within this context
        """
        # Push new context to stack
        new_context = LogContext(**kwargs)
        
        with self._context_lock:
            self._context_stack.append(new_context)
        
        try:
            yield self
        finally:
            # Remove context from stack
            with self._context_lock:
                if self._context_stack and self._context_stack[-1] is new_context:
                    self._context_stack.pop()
    
    def bind(self, **kwargs) -> "StructuredLogger":
        """Create a new logger with additional context."""
        new_logger = StructuredLogger(self.base_logger)
        
        # Copy global context
        new_logger._global_context = self._global_context
        
        # Create new context with additional values
        current_context = self._get_current_context()
        for key, value in kwargs.items():
            if hasattr(current_context, key):
                setattr(current_context, key, value)
            else:
                current_context.metadata[key] = value
        
        new_logger._context_stack = [current_context]
        return new_logger
    
    def _get_current_context(self) -> LogContext:
        """Get current context from stack or global context."""
        with self._context_lock:
            if self._context_stack:
                return self._context_stack[-1]
            else:
                return self._global_context
    
    def _get_context_dict(self) -> Dict[str, Any]:
        """Get merged context dictionary."""
        context = self._get_current_context()
        return context.to_dict()
    
    def _log_with_context(self, level: str, message: str, **kwargs) -> None:
        """Log message with current context."""
        context_dict = self._get_context_dict()
        context_dict.update(kwargs)
        
        getattr(self.base_logger, level)(message, **context_dict)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context."""
        self._log_with_context("debug", message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with context."""
        self._log_with_context("info", message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context."""
        self._log_with_context("warning", message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with context."""
        self._log_with_context("error", message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with context."""
        self._log_with_context("critical", message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with context."""
        self._log_with_context("exception", message, **kwargs)
    
    def log_event(self, event_name: str, level: str = "info", **kwargs) -> None:
        """Log structured event.
        
        Args:
            event_name: Name of the event
            level: Log level
            **kwargs: Event data
        """
        event_data = {"event": event_name}
        event_data.update(kwargs)
        self._log_with_context(level, f"Event: {event_name}", **event_data)
    
    def log_metric(self, metric_name: str, value: float, unit: Optional[str] = None, **kwargs) -> None:
        """Log metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            **kwargs: Additional metric metadata
        """
        metric_data = {
            "metric": metric_name,
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        
        if unit:
            metric_data["unit"] = unit
        
        metric_data.update(kwargs)
        
        self.info(f"Metric: {metric_name}", **metric_data)
    
    def log_audit_event(self, action: str, resource: Optional[str] = None, **kwargs) -> None:
        """Log audit event for security/compliance.
        
        Args:
            action: Action performed
            resource: Resource acted upon
            **kwargs: Additional audit data
        """
        audit_data = {
            "audit_event": True,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        if resource:
            audit_data["resource"] = resource
        
        audit_data.update(kwargs)
        
        self.warning(f"Audit: {action}", **audit_data)


class ContextManager:
    """Global context manager for structured logging."""
    
    def __init__(self):
        """Initialize global context manager."""
        self._contexts: Dict[str, LogContext] = {}
        self._lock = threading.Lock()
        
        # Default context
        self._contexts["default"] = LogContext()
    
    def create_context(
        self,
        name: str,
        request_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Create and register a new context.
        
        Args:
            name: Context name
            request_id: Optional request ID (generated if not provided)
            **kwargs: Context values
            
        Returns:
            Context ID
        """
        context_id = request_id or str(uuid.uuid4())
        
        context = LogContext(
            request_id=context_id,
            **kwargs
        )
        
        with self._lock:
            self._contexts[name] = context
        
        return context_id
    
    def get_context(self, name: str = "default") -> LogContext:
        """Get context by name.
        
        Args:
            name: Context name
            
        Returns:
            Log context
        """
        with self._lock:
            return self._contexts.get(name, self._contexts["default"])
    
    def update_context(self, name: str, **kwargs) -> None:
        """Update context values.
        
        Args:
            name: Context name
            **kwargs: Values to update
        """
        with self._lock:
            if name in self._contexts:
                context = self._contexts[name]
                for key, value in kwargs.items():
                    if hasattr(context, key):
                        setattr(context, key, value)
                    else:
                        context.metadata[key] = value
    
    def remove_context(self, name: str) -> None:
        """Remove context.
        
        Args:
            name: Context name
        """
        with self._lock:
            self._contexts.pop(name, None)
    
    def cleanup_contexts(self) -> None:
        """Remove all contexts except default."""
        with self._lock:
            default = self._contexts.get("default")
            self._contexts.clear()
            if default:
                self._contexts["default"] = default


# Global context manager
context_manager = ContextManager()


def structured_logger(name: str = "assistant", **kwargs) -> StructuredLogger:
    """Create structured logger instance.
    
    Args:
        name: Logger name
        **kwargs: Additional logger configuration
        
    Returns:
        Structured logger instance
    """
    from .logging import get_logger
    
    base_logger = get_logger(name, **kwargs)
    return StructuredLogger(base_logger)


def with_logging_context(
    context_name: Optional[str] = None,
    request_id: Optional[str] = None,
    **context_kwargs
):
    """Decorator to add logging context to functions.
    
    Args:
        context_name: Context name to use
        request_id: Request ID for the context
        **context_kwargs: Context data
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create context if name provided
            if context_name:
                context_id = context_manager.create_context(
                    context_name,
                    request_id=request_id,
                    **context_kwargs
                )
            else:
                context_id = None
            
            try:
                # Get structured logger
                logger = structured_logger(func.__module__)
                
                # Log function start
                logger.info(
                    f"Function started: {func.__name__}",
                    function=func.__name__,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys())
                )
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Log function completion
                logger.info(
                    f"Function completed: {func.__name__}",
                    function=func.__name__,
                    result_type=type(result).__name__
                )
                
                return result
                
            except Exception as e:
                # Log function error
                logger.exception(
                    f"Function failed: {func.__name__}",
                    function=func.__name__,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                
                raise
            
            finally:
                # Clean up context if created
                if context_id and context_name:
                    context_manager.remove_context(context_name)
        
        return wrapper
    return decorator


def log_correlation_id(correlation_id: Optional[str] = None):
    """Decorator to add correlation ID to logging context.
    
    Args:
        correlation_id: Correlation ID to use (generated if not provided)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cid = correlation_id or str(uuid.uuid4())
            
            # Get structured logger and bind correlation ID
            logger = structured_logger(func.__module__)
            correlated_logger = logger.bind(correlation_id=cid)
            
            # Add correlation ID to function kwargs for downstream use
            kwargs["_correlation_id"] = cid
            
            # Log with correlation context
            correlated_logger.info(
                f"Function with correlation: {func.__name__}",
                function=func.__name__,
                correlation_id=cid
            )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class StructuredLogFilter:
    """Filter for structured log events."""
    
    def __init__(self, required_fields: Optional[List[str]] = None):
        """Initialize filter.
        
        Args:
            required_fields: Fields that must be present in log records
        """
        self.required_fields = required_fields or []
    
    def filter(self, record: Any) -> bool:
        """Filter log record based on required fields.
        
        Args:
            record: Log record to filter
            
        Returns:
            True if record should be logged
        """
        if not self.required_fields:
            return True
        
        for field in self.required_fields:
            if not hasattr(record, field) or getattr(record, field) is None:
                return False
        
        return True
    
    def filter_by_context(self, context_keys: Optional[List[str]] = None, context_values: Optional[Dict[str, Any]] = None):
        """Create a filter that checks context values.
        
        Args:
            context_keys: Context keys that must be present
            context_values: Context key-value pairs that must match
            
        Returns:
            Filter function
        """
        def context_filter(record: Any) -> bool:
            # Check if record has structured context
            if not hasattr(record, 'context'):
                return False
            
            context = record.context if isinstance(record.context, dict) else {}
            
            # Check required keys
            if context_keys:
                for key in context_keys:
                    if key not in context:
                        return False
            
            # Check specific values
            if context_values:
                for key, value in context_values.items():
                    if context.get(key) != value:
                        return False
            
            return True
        
        return context_filter