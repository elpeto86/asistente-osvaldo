"""Exception logging utilities with stack trace capture and analysis."""

import traceback
import sys
import inspect
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from contextlib import contextmanager
import json
import re

from .logging import AssistantLogger
from .structured_logging import StructuredLogger


@dataclass
class ExceptionInfo:
    """Detailed exception information."""
    
    exception_type: str
    exception_message: str
    exception_module: str
    exception_line: Optional[int] = None
    exception_file: Optional[str] = None
    function_name: Optional[str] = None
    traceback_text: str = ""
    stack_trace: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception info to dictionary."""
        return {
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
            "exception_module": self.exception_module,
            "exception_line": self.exception_line,
            "exception_file": self.exception_file,
            "function_name": self.function_name,
            "traceback_text": self.traceback_text,
            "stack_trace": self.stack_trace,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }


class ExceptionLogger:
    """Enhanced logger for exception handling and analysis."""
    
    def __init__(self, base_logger: Union[AssistantLogger, StructuredLogger]):
        """Initialize exception logger.
        
        Args:
            base_logger: Base logger to use for exception logging
        """
        self.base_logger = base_logger
        self._exception_history: List[ExceptionInfo] = []
        self._exception_patterns: Dict[str, int] = {}
        self._lock = threading.Lock()
    
    def capture_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        include_traceback: bool = True
    ) -> ExceptionInfo:
        """Capture detailed exception information.
        
        Args:
            exception: Exception to capture
            context: Additional context information
            include_traceback: Whether to include full traceback
            
        Returns:
            Exception information
        """
        tb = exception.__traceback__
        
        if tb:
            # Get the top-level exception info
            frame = tb.tb_frame
            while frame.f_back:
                frame = frame.f_back
            
            exception_info = ExceptionInfo(
                exception_type=type(exception).__name__,
                exception_message=str(exception),
                exception_module=exception.__class__.__module__,
                exception_line=tb.tb_lineno if tb else None,
                exception_file=tb.tb_frame.f_code.co_filename if tb else None,
                function_name=tb.tb_frame.f_code.co_name if tb else None,
                context=context or {}
            )
            
            # Extract full traceback
            if include_traceback and tb:
                exception_info.traceback_text = "".join(
                    traceback.format_exception(type(exception), exception, tb)
                )
                
                # Parse stack trace
                exception_info.stack_trace = self._parse_stack_trace(tb)
        else:
            exception_info = ExceptionInfo(
                exception_type=type(exception).__name__,
                exception_message=str(exception),
                exception_module=exception.__class__.__module__,
                context=context or {}
            )
        
        # Store in history
        with self._lock:
            self._exception_history.append(exception_info)
            
            # Track exception patterns
            pattern_key = f"{exception_info.exception_type}:{exception_info.function_name}"
            self._exception_patterns[pattern_key] = self._exception_patterns.get(pattern_key, 0) + 1
            
            # Keep history manageable
            if len(self._exception_history) > 500:
                self._exception_history = self._exception_history[-500:]
        
        return exception_info
    
    def _parse_stack_trace(self, tb) -> List[Dict[str, Any]]:
        """Parse traceback into structured stack trace.
        
        Args:
            tb: Traceback object
            
        Returns:
            Structured stack trace
        """
        stack_trace = []
        current_tb = tb
        
        while current_tb:
            frame = current_tb.tb_frame
            code = frame.f_code
            
            # Extract local variables (be careful with sensitive data)
            local_vars = {}
            for name, value in frame.f_locals.items():
                # Skip built-ins and potentially sensitive data
                if not name.startswith('__') and not self._is_sensitive_name(name):
                    try:
                        local_vars[name] = self._safe_serialize(value)
                    except Exception:
                        local_vars[name] = "<unserializable>"
            
            stack_info = {
                "filename": code.co_filename,
                "function": code.co_name,
                "line_number": current_tb.tb_lineno,
                "line_content": self._get_line_content(code.co_filename, current_tb.tb_lineno),
                "local_vars": local_vars
            }
            
            stack_trace.append(stack_info)
            current_tb = current_tb.tb_next
        
        return stack_trace
    
    def _is_sensitive_name(self, name: str) -> bool:
        """Check if variable name might contain sensitive data."""
        sensitive_patterns = [
            'password', 'secret', 'key', 'token', 'auth', 'credentials',
            'private', 'confidential'
        ]
        
        name_lower = name.lower()
        return any(pattern in name_lower for pattern in sensitive_patterns)
    
    def _safe_serialize(self, obj: Any, max_length: int = 200) -> Any:
        """Safely serialize object for logging.
        
        Args:
            obj: Object to serialize
            max_length: Maximum string length
            
        Returns:
            Serialized object
        """
        try:
            if obj is None:
                return None
            elif isinstance(obj, (str, int, float, bool)):
                result = str(obj)
                return result[:max_length] + "..." if len(result) > max_length else result
            elif isinstance(obj, (list, tuple, set)):
                result = [self._safe_serialize(item, max_length) for item in list(obj)[:10]]
                return result
            elif isinstance(obj, dict):
                result = {}
                for key, value in list(obj.items())[:10]:
                    result[key] = self._safe_serialize(value, max_length)
                return result
            else:
                # For complex objects, just show type and representation
                result = f"{type(obj).__name__}: {repr(obj)[:max_length]}"
                return result
        except Exception:
            return f"<{type(obj).__name__, could not serialize}>"
    
    def _get_line_content(self, filename: str, line_number: int) -> Optional[str]:
        """Get content of specific line from file.
        
        Args:
            filename: File path
            line_number: Line number
            
        Returns:
            Line content or None if file not found
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if 1 <= line_number <= len(lines):
                    return lines[line_number - 1].strip()
        except Exception:
            pass
        return None
    
    def log_exception(
        self,
        exception: Exception,
        level: str = "error",
        context: Optional[Dict[str, Any]] = None,
        include_traceback: bool = True,
        **kwargs
    ) -> None:
        """Log exception with full details.
        
        Args:
            exception: Exception to log
            level: Log level
            context: Additional context
            include_traceback: Whether to include traceback
            **kwargs: Additional logging data
        """
        exception_info = self.capture_exception(exception, context, include_traceback)
        
        # Prepare log data
        log_data = exception_info.to_dict()
        log_data.update(kwargs)
        
        # Log with appropriate level
        getattr(self.base_logger, level)(
            f"Exception occurred: {exception_info.exception_type}",
            **log_data
        )
    
    def log_exception_with_context(
        self,
        exception: Exception,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        component: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log exception with common context fields.
        
        Args:
            exception: Exception to log
            user_id: User identifier
            request_id: Request identifier
            component: Component name
            **kwargs: Additional context
        """
        context = {}
        if user_id:
            context["user_id"] = user_id
        if request_id:
            context["request_id"] = request_id
        if component:
            context["component"] = component
        
        context.update(kwargs)
        
        self.log_exception(exception, context=context)
    
    def analyze_exception(self, exception: str) -> Dict[str, Any]:
        """Analyze exception patterns.
        
        Args:
            exception: Exception type to analyze
            
        Returns:
            Analysis results
        """
        with self._lock:
            related_exceptions = [
                exc for exc in self._exception_history
                if exc.exception_type == exception
            ]
        
        if not related_exceptions:
            return {"message": "No exceptions found of this type"}
        
        # Analyze patterns
        times = [exc.timestamp for exc in related_exceptions]
        functions = [exc.function_name for exc in related_exceptions if exc.function_name]
        files = [exc.exception_file for exc in related_exceptions if exc.exception_file]
        
        analysis = {
            "total_count": len(related_exceptions),
            "first_occurrence": min(times).isoformat(),
            "last_occurrence": max(times).isoformat(),
            "most_common_function": max(set(functions), key=functions.count) if functions else None,
            "most_common_file": max(set(files), key=files.count) if files else None,
            "unique_functions": list(set(functions)),
            "unique_files": list(set(files))
        }
        
        return analysis
    
    def get_exception_summary(self) -> Dict[str, Any]:
        """Get summary of all exceptions.
        
        Returns:
            Exception summary
        """
        with self._lock:
            summary = {
                "total_exceptions": len(self._exception_history),
                "exception_count_by_type": {},
                "most_common_exceptions": [],
                "recent_exceptions": []
            }
            
            # Count by type
            for exc in self._exception_history:
                exc_type = exc.exception_type
                summary["exception_count_by_type"][exc_type] = (
                    summary["exception_count_by_type"].get(exc_type, 0) + 1
                )
            
            # Most common exceptions
            summary["most_common_exceptions"] = [
                {"type": exc_type, "count": count}
                for exc_type, count in sorted(
                    summary["exception_count_by_type"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            ]
            
            # Recent exceptions (last 10)
            recent = sorted(self._exception_history, key=lambda x: x.timestamp, reverse=True)[:10]
            summary["recent_exceptions"] = [
                {
                    "type": exc.exception_type,
                    "message": exc.exception_message,
                    "function": exc.function_name,
                    "timestamp": exc.timestamp.isoformat()
                }
                for exc in recent
            ]
        
        return summary
    
    def clear_history(self) -> None:
        """Clear exception history."""
        with self._lock:
            self._exception_history.clear()
            self._exception_patterns.clear()


def exception_logger(
    reraise: bool = True,
    log_args: bool = False,
    context_data: Optional[Dict[str, Any]] = None
):
    """Decorator for automatic exception logging.
    
    Args:
        reraise: Whether to reraise exception after logging
        log_args: Whether to log function arguments
        context_data: Additional context data
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create exception logger
            logger = ExceptionLogger(StructuredLogger(get_logger(func.__module__)))
            
            # Prepare context
            context = context_data.copy() if context_data else {}
            
            if log_args:
                context["function_args_count"] = len(args)
                context["function_kwargs_keys"] = list(kwargs.keys())
            
            # Add function info
            context["function_name"] = func.__name__
            context["function_module"] = func.__module__
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.log_exception(
                    e,
                    context=context,
                    function=func.__name__,
                    module=func.__module__
                )
                
                if reraise:
                    raise
                else:
                    return None
        
        return wrapper
    return decorator


@contextmanager
def exception_context(
    operation: str,
    logger: Optional[ExceptionLogger] = None,
    **context_data
):
    """Context manager for exception logging.
    
    Args:
        operation: Operation name
        logger: Exception logger instance
        **context_data: Additional context data
    """
    if logger is None:
        logger = ExceptionLogger(StructuredLogger(get_logger("assistant.exceptions")))
    
    context = context_data.copy()
    context["operation"] = operation
    
    try:
        yield
    except Exception as e:
        logger.log_exception(
            e,
            context=context
        )
        raise


def safe_execute(
    func: Callable,
    *args,
    default: Any = None,
    log_exceptions: bool = True,
    **kwargs
) -> Any:
    """Safely execute function with exception handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        default: Default return value if exception occurs
        log_exceptions: Whether to log exceptions
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_exceptions:
            logger = ExceptionLogger(StructuredLogger(get_logger("assistant.exceptions")))
            logger.log_exception(
                e,
                context={
                    "function": func.__name__,
                    "module": func.__module__
                }
            )
        return default


class ExceptionHandler:
    """Base class for handling specific exception types."""
    
    def __init__(self, exception_types: List[type]):
        """Initialize exception handler.
        
        Args:
            exception_types: List of exception types to handle
        """
        self.exception_types = exception_types
    
    def can_handle(self, exception: Exception) -> bool:
        """Check if handler can handle this exception.
        
        Args:
            exception: Exception to check
            
        Returns:
            True if handler can handle exception
        """
        return type(exception) in self.exception_types
    
    def handle(self, exception: Exception, context: Optional[Dict[str, Any]] = None) -> Any:
        """Handle exception.
        
        Args:
            exception: Exception to handle
            context: Optional context
            
        Returns:
            Handler result
        """
        raise NotImplementedError


# Global exception logger instance
_global_exception_logger: Optional[ExceptionLogger] = None


def get_global_exception_logger() -> ExceptionLogger:
    """Get global exception logger instance."""
    global _global_exception_logger
    
    if _global_exception_logger is None:
        logger = get_logger("assistant.exceptions")
        _global_exception_logger = ExceptionLogger(logger)
    
    return _global_exception_logger


# Import at module level to avoid circular imports
from .structured_logging import structured_logger as get_logger
import threading