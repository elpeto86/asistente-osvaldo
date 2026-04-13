"""Performance logging utilities for monitoring and optimization."""

import time
import threading
import statistics
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
from contextlib import contextmanager
import json

from .logging import AssistantLogger
from .structured_logging import StructuredLogger


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    
    operation: str
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Optional metrics
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    request_size_bytes: Optional[int] = None
    response_size_bytes: Optional[int] = None
    cache_hit: Optional[bool] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        data = {
            "operation": self.operation,
            "duration_ms": round(self.duration_ms, 2),
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            **self.metadata
        }
        
        # Add optional metrics if present
        for attr in ["memory_usage_mb", "cpu_usage_percent", "request_size_bytes", 
                     "response_size_bytes", "cache_hit"]:
            value = getattr(self, attr)
            if value is not None:
                data[attr] = value
        
        return data


class PerformanceLogger:
    """Logger for performance metrics and monitoring."""
    
    def __init__(self, base_logger: Union[AssistantLogger, StructuredLogger]):
        """Initialize performance logger.
        
        Args:
            base_logger: Base logger to use for performance logging
        """
        self.base_logger = base_logger
        self._metrics_history: List[PerformanceMetrics] = []
        self._operation_stats: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
        
        # Performance thresholds
        self._thresholds: Dict[str, float] = {
            "warning": 1000.0,  # 1 second
            "critical": 5000.0,  # 5 seconds
        }
    
    def set_thresholds(self, warning_ms: float = 1000.0, critical_ms: float = 5000.0) -> None:
        """Set performance thresholds for automated logging.
        
        Args:
            warning_ms: Warning threshold in milliseconds
            critical_ms: Critical threshold in milliseconds
        """
        self._thresholds["warning"] = warning_ms
        self._thresholds["critical"] = critical_ms
    
    def log_performance(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        **metadata
    ) -> None:
        """Log performance metrics.
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            success: Whether operation was successful
            **metadata: Additional performance data
        """
        # Create metrics record
        metrics = PerformanceMetrics(
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            metadata=metadata
        )
        
        # Store in history
        with self._lock:
            self._metrics_history.append(metrics)
            
            if operation not in self._operation_stats:
                self._operation_stats[operation] = []
            self._operation_stats[operation].append(duration_ms)
            
            # Keep history manageable (last 1000 entries)
            if len(self._metrics_history) > 1000:
                self._metrics_history = self._metrics_history[-1000:]
            
            # Keep operation stats manageable (last 100 entries per operation)
            if len(self._operation_stats[operation]) > 100:
                self._operation_stats[operation] = self._operation_stats[operation][-100:]
        
        # Log with appropriate level based on thresholds
        log_data = {
            "operation": operation,
            "duration_ms": round(duration_ms, 2),
            "success": success,
            **metadata
        }
        
        if not success:
            self.base_logger.error("Performance: Operation failed", **log_data)
        elif duration_ms > self._thresholds["critical"]:
            self.base_logger.critical("Performance: Operation critical", **log_data)
        elif duration_ms > self._thresholds["warning"]:
            self.base_logger.warning("Performance: Operation slow", **log_data)
        else:
            self.base_logger.info("Performance: Operation completed", **log_data)
    
    @contextmanager
    def measure(self, operation: str, **metadata):
        """Context manager for measuring operation performance.
        
        Args:
            operation: Operation name
            **metadata: Additional metadata
            
        Yields:
            Context for the operation
        """
        start_time = time.time()
        success = True
        
        try:
            yield
        except Exception as e:
            success = False
            metadata["error_type"] = type(e).__name__
            metadata["error_message"] = str(e)
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.log_performance(operation, duration_ms, success, **metadata)
    
    def get_operation_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for a specific operation.
        
        Args:
            operation: Operation name
            
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            if operation not in self._operation_stats:
                return {}
            
            durations = self._operation_stats[operation]
            
            if not durations:
                return {}
            
            return {
                "count": len(durations),
                "min_ms": min(durations),
                "max_ms": max(durations),
                "avg_ms": statistics.mean(durations),
                "median_ms": statistics.median(durations),
                "p95_ms": self._percentile(durations, 95),
                "p99_ms": self._percentile(durations, 99),
            }
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))
        if index >= len(sorted_data):
            index = len(sorted_data) - 1
        
        return sorted_data[index]
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary of all performance statistics.
        
        Returns:
            Summary statistics dictionary
        """
        with self._lock:
            summary = {
                "total_operations": len(self._metrics_history),
                "operations": {},
                "overall_stats": {}
            }
            
            # Get stats for each operation
            for operation in self._operation_stats:
                summary["operations"][operation] = self.get_operation_stats(operation)
            
            # Calculate overall stats
            all_durations = []
            for durations in self._operation_stats.values():
                all_durations.extend(durations)
            
            if all_durations:
                summary["overall_stats"] = {
                    "total_operations": len(all_durations),
                    "avg_ms": statistics.mean(all_durations),
                    "median_ms": statistics.median(all_durations),
                    "p95_ms": self._percentile(all_durations, 95),
                    "p99_ms": self._percentile(all_durations, 99),
                }
            
            return summary
    
    def clear_history(self) -> None:
        """Clear performance history."""
        with self._lock:
            self._metrics_history.clear()
            self._operation_stats.clear()
    
    def export_metrics(self, format: str = "json") -> str:
        """Export performance metrics.
        
        Args:
            format: Export format ('json', 'csv')
            
        Returns:
            Formatted metrics string
        """
        summary = self.get_summary_stats()
        
        if format == "json":
            return json.dumps(summary, indent=2, default=str)
        elif format == "csv":
            # CSV format for operations
            lines = ["operation,count,min_ms,max_ms,avg_ms,median_ms,p95_ms,p99_ms"]
            
            for operation, stats in summary["operations"].items():
                lines.append(
                    f"{operation},{stats.get('count', 0)},{stats.get('min_ms', 0)},"
                    f"{stats.get('max_ms', 0)},{stats.get('avg_ms', 0):.2f},"
                    f"{stats.get('median_ms', 0):.2f},{stats.get('p95_ms', 0):.2f},"
                    f"{stats.get('p99_ms', 0):.2f}"
                )
            
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")


def performance_logger(
    operation_name: Optional[str] = None,
    log_args: bool = False,
    log_result: bool = False,
    **metadata
):
    """Decorator for automatic performance logging of functions.
    
    Args:
        operation_name: Operation name (function name used if not provided)
        log_args: Whether to log function arguments
        log_result: Whether to log function result
        **metadata: Additional metadata for all calls
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine operation name
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            # Get performance logger
            logger = PerformanceLogger(
                StructuredLogger(get_logger(func.__module__))
            )
            
            # Prepare metadata
            call_metadata = metadata.copy()
            
            if log_args:
                call_metadata["args_count"] = len(args)
                call_metadata["kwargs_keys"] = list(kwargs.keys())
            
            # Add more detailed argument metadata
            if args and hasattr(args[0], '__class__'):
                call_metadata["self_type"] = args[0].__class__.__name__
            
            # Measure performance
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                duration_ms = (time.time() - start_time) * 1000
                
                if log_result:
                    call_metadata["result_type"] = type(result).__name__
                    if hasattr(result, '__len__'):
                        call_metadata["result_size"] = len(result)
                
                logger.log_performance(op_name, duration_ms, True, **call_metadata)
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                call_metadata["error_type"] = type(e).__name__
                call_metadata["error_message"] = str(e)
                
                logger.log_performance(op_name, duration_ms, False, **call_metadata)
                
                raise
        
        return wrapper
    return decorator


class MemoryProfiler:
    """Memory profiling utilities."""
    
    def __init__(self, logger: Union[AssistantLogger, StructuredLogger]):
        """Initialize memory profiler.
        
        Args:
            logger: Logger to use for memory metrics
        """
        self.logger = logger
        
        try:
            import psutil
            self.psutil = psutil
            self.available = True
        except ImportError:
            self.available = False
    
    def get_memory_usage(self) -> Optional[float]:
        """Get current memory usage in MB.
        
        Returns:
            Memory usage in MB or None if psutil not available
        """
        if not self.available:
            return None
        
        process = self.psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def log_memory_usage(self, operation: str, **metadata) -> None:
        """Log current memory usage.
        
        Args:
            operation: Current operation
            **metadata: Additional metadata
        """
        memory_mb = self.get_memory_usage()
        
        if memory_mb is not None:
            log_data = {
                "operation": operation,
                "memory_usage_mb": round(memory_mb, 2),
                **metadata
            }
            
            if memory_mb > 1000:  # Warning threshold of 1GB
                self.logger.warning("Memory usage high", **log_data)
            else:
                self.logger.info("Memory usage", **log_data)
    
    @contextmanager
    def profile_memory(self, operation: str, **metadata):
        """Context manager for memory profiling.
        
        Args:
            operation: Operation name
            **metadata: Additional metadata
        """
        initial_memory = self.get_memory_usage()
        
        try:
            yield
        finally:
            final_memory = self.get_memory_usage()
            
            if initial_memory is not None and final_memory is not None:
                memory_delta = final_memory - initial_memory
                
                log_data = {
                    "operation": operation,
                    "initial_memory_mb": round(initial_memory, 2),
                    "final_memory_mb": round(final_memory, 2),
                    "memory_delta_mb": round(memory_delta, 2),
                    **metadata
                }
                
                if abs(memory_delta) > 100:  # Significant memory change
                    self.logger.warning("Memory delta significant", **log_data)
                else:
                    self.logger.info("Memory usage", **log_data)


# Global performance logger instance
_global_performance_logger: Optional[PerformanceLogger] = None


def get_global_performance_logger() -> PerformanceLogger:
    """Get global performance logger instance."""
    global _global_performance_logger
    
    if _global_performance_logger is None:
        import sys
        logger = get_logger("assistant.performance")
        _global_performance_logger = PerformanceLogger(logger)
    
    return _global_performance_logger


def log_performance(operation: str, duration_ms: float, success: bool = True, **metadata) -> None:
    """Log performance using global logger.
    
    Args:
        operation: Operation name
        duration_ms: Duration in milliseconds
        success: Whether operation was successful
        **metadata: Additional metadata
    """
    logger = get_global_performance_logger()
    logger.log_performance(operation, duration_ms, success, **metadata)


# Import at module level to avoid circular imports
from .structured_logging import structured_logger as get_logger