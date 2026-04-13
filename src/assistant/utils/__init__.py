"""Utility functions and helpers for the assistant framework.

This module provides:
- Enhanced logging system with multiple output formats
- Component-specific logger factory with decorators
- Structured logging with context management
- Performance monitoring and profiling utilities
- Exception logging with stack trace analysis
"""

from .logging import (
    AssistantLogger,
    LoggerManager,
    get_logger,
    configure_logging,
    logger_manager
)

from .logger_factory import (
    LoggerFactory,
    component_logger,
    get_component_logger,
    register_component_logging,
    log_method_calls
)

from .structured_logging import (
    LogContext,
    StructuredLogger,
    ContextManager,
    structured_logger,
    with_logging_context,
    log_correlation_id,
    StructuredLogFilter
)

from .performance_logger import (
    PerformanceMetrics,
    PerformanceLogger,
    performance_logger,
    MemoryProfiler,
    get_global_performance_logger,
    log_performance
)

from .exception_logger import (
    ExceptionInfo,
    ExceptionLogger,
    exception_logger,
    exception_context,
    safe_execute,
    ExceptionHandler,
    get_global_exception_logger
)

__all__ = [
    # Core logging
    "AssistantLogger",
    "LoggerManager", 
    "get_logger",
    "configure_logging",
    "logger_manager",
    
    # Component logging
    "LoggerFactory",
    "component_logger",
    "get_component_logger", 
    "register_component_logging",
    "log_method_calls",
    
    # Structured logging
    "LogContext",
    "StructuredLogger",
    "ContextManager",
    "structured_logger",
    "with_logging_context",
    "log_correlation_id",
    "StructuredLogFilter",
    
    # Performance logging
    "PerformanceMetrics",
    "PerformanceLogger",
    "performance_logger",
    "MemoryProfiler",
    "get_global_performance_logger",
    "log_performance",
    
    # Exception logging
    "ExceptionInfo",
    "ExceptionLogger,"
    "exception_logger",
    "exception_context", 
    "safe_execute",
    "ExceptionHandler",
    "get_global_exception_logger",
]