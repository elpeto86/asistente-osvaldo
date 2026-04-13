"""Message interface definitions for assistant communication."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid


class MessageType:
    """Message type constants."""
    USER = "user"
    ASSISTANT = "assistant" 
    SYSTEM = "system"
    TOOL = "tool"
    ERROR = "error"


@dataclass
class Message:
    """Base message class for assistant communication."""
    
    content: str
    message_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "content": self.content,
            "message_type": self.message_type,
            "timestamp": self.timestamp.isoformat(),
            "message_id": self.message_id,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        if isinstance(data["timestamp"], str):
            timestamp = datetime.fromisoformat(data["timestamp"])
        else:
            timestamp = data["timestamp"]
            
        return cls(
            content=data["content"],
            message_type=data["message_type"],
            timestamp=timestamp,
            message_id=data.get("message_id", str(uuid.uuid4())),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """Create message from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to message."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.message_type}: {self.content[:100]}"


@dataclass
class UserMessage(Message):
    """Message from user to assistant."""
    
    def __post_init__(self):
        """Ensure message type is set correctly."""
        self.message_type = MessageType.USER
    
    @classmethod
    def create(
        cls, 
        content: str, 
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **metadata
    ) -> "UserMessage":
        """Create user message with common metadata."""
        msg = cls(content=content)
        
        if user_id:
            msg.add_metadata("user_id", user_id)
        if session_id:
            msg.add_metadata("session_id", session_id)
        
        for key, value in metadata.items():
            msg.add_metadata(key, value)
            
        return msg


@dataclass
class AssistantMessage(Message):
    """Message from assistant to user."""
    
    confidence: float = 1.0
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Ensure message type is set correctly."""
        self.message_type = MessageType.ASSISTANT
    
    @classmethod
    def create(
        cls,
        content: str,
        confidence: float = 1.0,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        **metadata
    ) -> "AssistantMessage":
        """Create assistant message with common metadata."""
        msg = cls(
            content=content,
            confidence=confidence,
            tool_calls=tool_calls or []
        )
        
        if user_id:
            msg.add_metadata("user_id", user_id)
        if session_id:
            msg.add_metadata("session_id", session_id)
        
        for key, value in metadata.items():
            msg.add_metadata(key, value)
            
        return msg
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with confidence and tool calls."""
        base_dict = super().to_dict()
        base_dict.update({
            "confidence": self.confidence,
            "tool_calls": self.tool_calls
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssistantMessage":
        """Create from dictionary with confidence and tool calls."""
        if isinstance(data["timestamp"], str):
            timestamp = datetime.fromisoformat(data["timestamp"])
        else:
            timestamp = data["timestamp"]
            
        return cls(
            content=data["content"],
            message_type=data["message_type"],
            timestamp=timestamp,
            message_id=data.get("message_id", str(uuid.uuid4())),
            metadata=data.get("metadata", {}),
            confidence=data.get("confidence", 1.0),
            tool_calls=data.get("tool_calls", [])
        )


@dataclass
class SystemMessage(Message):
    """System message for configuration and control."""
    
    level: str = "info"  # debug, info, warning, error, critical
    target: Optional[str] = None  # Target component or user
    
    def __post_init__(self):
        """Ensure message type is set correctly."""
        self.message_type = MessageType.SYSTEM
    
    @classmethod
    def create(
        cls,
        content: str,
        level: str = "info",
        target: Optional[str] = None,
        **metadata
    ) -> "SystemMessage":
        """Create system message with common metadata."""
        msg = cls(content=content, level=level, target=target)
        
        for key, value in metadata.items():
            msg.add_metadata(key, value)
            
        return msg
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with level and target."""
        base_dict = super().to_dict()
        base_dict.update({
            "level": self.level,
            "target": self.target
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemMessage":
        """Create from dictionary with level and target."""
        if isinstance(data["timestamp"], str):
            timestamp = datetime.fromisoformat(data["timestamp"])
        else:
            timestamp = data["timestamp"]
            
        return cls(
            content=data["content"],
            message_type=data["message_type"],
            timestamp=timestamp,
            message_id=data.get("message_id", str(uuid.uuid4())),
            metadata=data.get("metadata", {}),
            level=data.get("level", "info"),
            target=data.get("target")
        )


@dataclass
class ToolMessage(Message):
    """Message from tool execution."""
    
    tool_name: str
    tool_args: Dict[str, Any]
    execution_time_ms: float = 0.0
    success: bool = True
    
    def __post_init__(self):
        """Ensure message type is set correctly."""
        self.message_type = MessageType.TOOL
    
    @classmethod
    def create(
        cls,
        tool_name: str,
        tool_args: Dict[str, Any],
        content: str,
        execution_time_ms: float = 0.0,
        success: bool = True,
        **metadata
    ) -> "ToolMessage":
        """Create tool message with common metadata."""
        msg = cls(
            content=content,
            tool_name=tool_name,
            tool_args=tool_args,
            execution_time_ms=execution_time_ms,
            success=success
        )
        
        for key, value in metadata.items():
            msg.add_metadata(key, value)
            
        return msg
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with tool info."""
        base_dict = super().to_dict()
        base_dict.update({
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "execution_time_ms": self.execution_time_ms,
            "success": self.success
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolMessage":
        """Create from dictionary with tool info."""
        if isinstance(data["timestamp"], str):
            timestamp = datetime.fromisoformat(data["timestamp"])
        else:
            timestamp = data["timestamp"]
            
        return cls(
            content=data["content"],
            message_type=data["message_type"],
            timestamp=timestamp,
            message_id=data.get("message_id", str(uuid.uuid4())),
            metadata=data.get("metadata", {}),
            tool_name=data["tool_name"],
            tool_args=data["tool_args"],
            execution_time_ms=data.get("execution_time_ms", 0.0),
            success=data.get("success", True)
        )


@dataclass
class ErrorMessage(Message):
    """Error message for exceptions and failures."""
    
    error_code: Optional[str] = None
    error_type: Optional[str] = None
    stack_trace: Optional[str] = None
    
    def __post_init__(self):
        """Ensure message type is set correctly."""
        self.message_type = MessageType.ERROR
    
    @classmethod
    def create(
        cls,
        content: str,
        error_code: Optional[str] = None,
        error_type: Optional[str] = None,
        stack_trace: Optional[str] = None,
        **metadata
    ) -> "ErrorMessage":
        """Create error message with common metadata."""
        msg = cls(
            content=content,
            error_code=error_code,
            error_type=error_type,
            stack_trace=stack_trace
        )
        
        for key, value in metadata.items():
            msg.add_metadata(key, value)
            
        return msg
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with error info."""
        base_dict = super().to_dict()
        base_dict.update({
            "error_code": self.error_code,
            "error_type": self.error_type,
            "stack_trace": self.stack_trace
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ErrorMessage":
        """Create from dictionary with error info."""
        if isinstance(data["timestamp"], str):
            timestamp = datetime.fromisoformat(data["timestamp"])
        else:
            timestamp = data["timestamp"]
            
        return cls(
            content=data["content"],
            message_type=data["message_type"],
            timestamp=timestamp,
            message_id=data.get("message_id", str(uuid.uuid4())),
            metadata=data.get("metadata", {}),
            error_code=data.get("error_code"),
            error_type=data.get("error_type"),
            stack_trace=data.get("stack_trace")
        )