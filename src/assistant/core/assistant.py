"""Base assistant abstract class for all AI assistant implementations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import asyncio
import time
from dataclasses import dataclass
from .config import Config
from ..interfaces.message import Message
from ..interfaces.responses import AssistantResponse


class AssistantStatus:
    """Assistant operational status."""
    
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    PAUSED = "paused"
    SHUTTING_DOWN = "shutting_down"


@dataclass
class AssistantMetrics:
    """Performance and operational metrics for the assistant."""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    uptime_seconds: float = 0.0
    last_request_time: Optional[float] = None
    
    def increment_success(self, response_time_ms: float) -> None:
        """Mark a successful request and update metrics."""
        self.total_requests += 1
        self.successful_requests += 1
        
        # Update average response time
        if self.total_requests == 1:
            self.average_response_time_ms = response_time_ms
        else:
            self.average_response_time_ms = (
                (self.average_response_time_ms * (self.total_requests - 1) + response_time_ms) / 
                self.total_requests
            )
        self.last_request_time = time.time()
    
    def increment_failure(self) -> None:
        """Mark a failed request."""
        self.total_requests += 1
        self.failed_requests += 1
        self.last_request_time = time.time()
    
    def update_uptime(self, start_time: float) -> None:
        """Update uptime calculation."""
        self.uptime_seconds = time.time() - start_time
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100


class BaseAssistant(ABC):
    """Abstract base class for AI assistant implementations.
    
    This class defines the common interface and functionality that all
    assistant implementations should follow. It provides configuration management,
    lifecycle management, and basic metrics tracking.
    """
    
    def __init__(self, config: Optional[Config] = None, **kwargs):
        """Initialize the assistant.
        
        Args:
            config: Configuration instance (generated if not provided)
            **kwargs: Additional configuration options
        """
        # Initialize configuration
        if config is None:
            from .config_loader import load_config_with_sources
            self.config = load_config_with_sources(**kwargs)
        else:
            self.config = config
        
        # Internal state
        self._status = AssistantStatus.INITIALIZING
        self._start_time = time.time()
        self._metrics = AssistantMetrics()
        self._context: Dict[str, Any] = {}
        self._event_handlers: Dict[str, List[callable]] = {}
        
        # Initialize the assistant
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize internal state and call configure method."""
        try:
            self.configure()
            self._status = AssistantStatus.READY
            self._emit_event("initialized", {"assistant": self.name})
        except Exception as e:
            self._status = AssistantStatus.ERROR
            self._emit_event("error", {"error": str(e)})
            raise
    
    @property
    def name(self) -> str:
        """Get assistant name from configuration."""
        return self.config.name
    
    @property
    def status(self) -> str:
        """Get current assistant status."""
        return self._status
    
    @property
    def metrics(self) -> AssistantMetrics:
        """Get assistant metrics."""
        self._metrics.update_uptime(self._start_time)
        return self._metrics
    
    @property
    def context(self) -> Dict[str, Any]:
        """Get assistant context data."""
        return self._context.copy()
    
    @abstractmethod
    def process_input(self, message: Union[Message, str, dict], **kwargs) -> AssistantResponse:
        """Process user input and generate response.
        
        Args:
            message: User message to process
            **kwargs: Additional processing options
            
        Returns:
            Assistant response
            
        Raises:
            NotImplementedError: Must be implemented by subclass
            AssistantError: If processing fails
        """
        pass
    
    @abstractmethod
    def configure(self) -> None:
        """Configure the assistant with settings and resources.
        
        This method should set up any required resources, initialize models,
        and perform any other setup tasks needed before the assistant can
        start processing requests.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources and shutdown the assistant.
        
        This method should release any resources, close connections,
        and perform any other cleanup tasks before shutdown.
        """
        pass
    
    def process_input_async(self, message: Union[Message, str, dict], **kwargs) -> 'Future[AssistantResponse]':
        """Asynchronous wrapper for process_input method.
        
        Args:
            message: User message to process
            **kwargs: Additional processing options
            
        Returns:
            Future containing assistant response
        """
        return asyncio.get_event_loop().run_in_executor(
            None, self.process_input, message, **kwargs
        )
    
    def set_context_value(self, key: str, value: Any) -> None:
        """Set a value in the assistant context.
        
        Args:
            key: Context key
            value: Value to store
        """
        self._context[key] = value
    
    def get_context_value(self, key: str, default: Any = None) -> Any:
        """Get a value from the assistant context.
        
        Args:
            key: Context key
            default: Default value if key not found
            
        Returns:
            Context value or default
        """
        return self._context.get(key, default)
    
    def clear_context(self) -> None:
        """Clear all context data."""
        self._context.clear()
        self._emit_event("context_cleared", {})
    
    def add_event_handler(self, event: str, handler: callable) -> None:
        """Add an event handler.
        
        Args:
            event: Event name
            handler: Handler function
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    def remove_event_handler(self, event: str, handler: callable) -> bool:
        """Remove an event handler.
        
        Args:
            event: Event name
            handler: Handler function to remove
            
        Returns:
            True if handler was removed, False if not found
        """
        if event in self._event_handlers:
            try:
                self._event_handlers[event].remove(handler)
                return True
            except ValueError:
                pass
        return False
    
    def _emit_event(self, event: str, data: Dict[str, Any]) -> None:
        """Emit an event to all registered handlers.
        
        Args:
            event: Event name
            data: Event data
        """
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                handler(event, data)
            except Exception:
                # Log error but don't stop other handlers
                pass
    
    def update_status(self, status: str) -> None:
        """Update assistant status and emit event.
        
        Args:
            status: New status value
        """
        old_status = self._status
        self._status = status
        self._emit_event("status_changed", {
            "old_status": old_status,
            "new_status": status
        })
    
    def reset_metrics(self) -> None:
        """Reset all metrics to initial values."""
        self._metrics = AssistantMetrics()
        self._start_time = time.time()
        self._emit_event("metrics_reset", {})
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status information.
        
        Returns:
            Health status dictionary
        """
        return {
            "status": self._status,
            "name": self.name,
            "uptime_seconds": self.metrics.uptime_seconds,
            "success_rate": self.metrics.success_rate,
            "total_requests": self.metrics.total_requests,
            "last_request_time": self.metrics.last_request_time,
        }
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        try:
            self.cleanup()
        except Exception:
            pass  # Don't raise during cleanup
    
    def __repr__(self) -> str:
        """String representation of assistant."""
        return f"{self.__class__.__name__}(name='{self.name}', status='{self._status}')"


class AssistantError(Exception):
    """Base exception for assistant-related errors."""
    pass


class ConfigurationError(AssistantError):
    """Raised when assistant configuration is invalid."""
    pass


class ProcessingError(AssistantError):
    """Raised when input processing fails."""
    pass


class ResourceError(AssistantError):
    """Raised when required resources are unavailable."""
    pass