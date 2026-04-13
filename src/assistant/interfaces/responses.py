"""Response classes for assistant outputs."""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from datetime import datetime
import uuid


class ResponseStatus(Enum):
    """Response status enumeration."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class AssistantResponse:
    """Standard response from assistant processing."""
    
    content: str
    status: ResponseStatus = ResponseStatus.SUCCESS
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    execution_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        """Validate response after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        if self.execution_time_ms < 0:
            raise ValueError("Execution time cannot be negative")
    
    @classmethod
    def create_success(
        cls,
        content: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        sources: Optional[List[Dict[str, Any]]] = None,
        execution_time_ms: Optional[float] = None,
        **kwargs
    ) -> "AssistantResponse":
        """Create a successful response."""
        return cls(
            content=content,
            status=ResponseStatus.SUCCESS,
            confidence=confidence,
            metadata=metadata or {},
            sources=sources or [],
            execution_time_ms=execution_time_ms or 0.0,
            **kwargs
        )
    
    @classmethod
    def create_error(
        cls,
        content: str,
        error_code: Optional[str] = None,
        error_type: Optional[str] = None,
        execution_time_ms: Optional[float] = None,
        **kwargs
    ) -> "AssistantResponse":
        """Create an error response."""
        metadata = kwargs.pop("metadata", {})
        if error_code:
            metadata["error_code"] = error_code
        if error_type:
            metadata["error_type"] = error_type
        
        return cls(
            content=content,
            status=ResponseStatus.ERROR,
            metadata=metadata,
            execution_time_ms=execution_time_ms or 0.0,
            **kwargs
        )
    
    @classmethod
    def create_partial(
        cls,
        content: str,
        confidence: float = 0.5,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "AssistantResponse":
        """Create a partial response."""
        merged_metadata = metadata or {}
        if reason:
            merged_metadata["partial_reason"] = reason
        
        return cls(
            content=content,
            status=ResponseStatus.PARTIAL,
            confidence=confidence,
            metadata=merged_metadata,
            **kwargs
        )
    
    def is_success(self) -> bool:
        """Check if response is successful."""
        return self.status == ResponseStatus.SUCCESS
    
    def is_error(self) -> bool:
        """Check if response indicates error."""
        return self.status == ResponseStatus.ERROR
    
    def is_complete(self) -> bool:
        """Check if response is complete (not partial)."""
        return self.status != ResponseStatus.PARTIAL
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to response."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)
    
    def add_source(self, source: Dict[str, Any]) -> None:
        """Add a source reference."""
        self.sources.append(source)
    
    def get_sources_by_type(self, source_type: str) -> List[Dict[str, Any]]:
        """Get sources of specific type."""
        return [s for s in self.sources if s.get("type") == source_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "content": self.content,
            "status": self.status.value,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "sources": self.sources,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "response_id": self.response_id
        }
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """Convert response to JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssistantResponse":
        """Create response from dictionary."""
        # Handle timestamp conversion
        if isinstance(data["timestamp"], str):
            timestamp = datetime.fromisoformat(data["timestamp"])
        else:
            timestamp = data["timestamp"]
        
        # Handle status conversion
        if isinstance(data["status"], str):
            status = ResponseStatus(data["status"])
        else:
            status = data["status"]
        
        return cls(
            content=data["content"],
            status=status,
            confidence=data.get("confidence", 1.0),
            metadata=data.get("metadata", {}),
            sources=data.get("sources", []),
            execution_time_ms=data.get("execution_time_ms", 0.0),
            timestamp=timestamp,
            response_id=data.get("response_id", str(uuid.uuid4()))
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "AssistantResponse":
        """Create response from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """String representation."""
        status_symbol = "✓" if self.is_success() else "✗" if self.is_error() else "~"
        return f"{status_symbol} {self.content[:100]} (confidence: {self.confidence:.2f})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"AssistantResponse(status={self.status.value}, "
                f"confidence={self.confidence}, "
                f"content_length={len(self.content)})")


@dataclass
class StreamResponse:
    """Response for streaming real-time output."""
    
    content: str
    finished: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunk_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "finished": self.finished,
            "metadata": self.metadata,
            "chunk_id": self.chunk_id,
            "timestamp": self.timestamp.isoformat()
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StreamResponse":
        """Create from dictionary."""
        if isinstance(data["timestamp"], str):
            timestamp = datetime.fromisoformat(data["timestamp"])
        else:
            timestamp = data["timestamp"]
            
        return cls(
            content=data["content"],
            finished=data["finished"],
            metadata=data.get("metadata", {}),
            chunk_id=data.get("chunk_id", str(uuid.uuid4())),
            timestamp=timestamp
        )
    
    def __str__(self) -> str:
        """String representation."""
        end_marker = " [END]" if self.finished else ""
        return f"{self.content}{end_marker}"


class ResponseBuilder:
    """Builder pattern for creating AssistantResponse objects."""
    
    def __init__(self):
        """Initialize response builder."""
        self._content = ""
        self._status = ResponseStatus.SUCCESS
        self._confidence = 1.0
        self._metadata = {}
        self._sources = []
        self._execution_time_ms = 0.0
        self._start_time = None
    
    def content(self, content: str) -> "ResponseBuilder":
        """Set response content."""
        self._content = content
        return self
    
    def status(self, status: ResponseStatus) -> "ResponseBuilder":
        """Set response status."""
        self._status = status
        return self
    
    def confidence(self, confidence: float) -> "ResponseBuilder":
        """Set confidence level."""
        self._confidence = confidence
        return self
    
    def add_metadata(self, key: str, value: Any) -> "ResponseBuilder":
        """Add metadata."""
        self._metadata[key] = value
        return self
    
    def metadata(self, metadata: Dict[str, Any]) -> "ResponseBuilder":
        """Set all metadata."""
        self._metadata = metadata
        return self
    
    def add_source(self, source: Dict[str, Any]) -> "ResponseBuilder":
        """Add source reference."""
        self._sources.append(source)
        return self
    
    def sources(self, sources: List[Dict[str, Any]]) -> "ResponseBuilder":
        """Set all sources."""
        self._sources = sources
        return self
    
    def start_timing(self) -> "ResponseBuilder":
        """Start execution timing."""
        self._start_time = time.time()
        return self
    
    def stop_timing(self) -> "ResponseBuilder":
        """Stop execution timing."""
        if self._start_time is not None:
            self._execution_time_ms = (time.time() - self._start_time) * 1000
        return self
    
    def execution_time(self, time_ms: float) -> "ResponseBuilder":
        """Set execution time directly."""
        self._execution_time_ms = time_ms
        return self
    
    def build(self) -> AssistantResponse:
        """Build the AssistantResponse."""
        return AssistantResponse(
            content=self._content,
            status=self._status,
            confidence=self._confidence,
            metadata=self._metadata.copy(),
            sources=self._sources.copy(),
            execution_time_ms=self._execution_time_ms
        )
    
    def build_error(
        self, 
        error_message: str, 
        error_code: Optional[str] = None,
        error_type: Optional[str] = None
    ) -> AssistantResponse:
        """Build an error response."""
        if error_code:
            self.add_metadata("error_code", error_code)
        if error_type:
            self.add_metadata("error_type", error_type)
        
        return self.error_status().content(error_message).build()
    
    def success_status(self) -> "ResponseBuilder":
        """Set status to success."""
        return self.status(ResponseStatus.SUCCESS)
    
    def error_status(self) -> "ResponseBuilder":
        """Set status to error."""
        return self.status(ResponseStatus.ERROR)
    
    def partial_status(self) -> "ResponseBuilder":
        """Set status to partial."""
        return self.status(ResponseStatus.PARTIAL)