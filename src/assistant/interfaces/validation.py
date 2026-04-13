"""Message validation and serialization utilities."""

import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import re
from dataclasses import asdict, fields

from .message import Message, UserMessage, AssistantMessage, SystemMessage, ToolMessage, ErrorMessage
from .responses import AssistantResponse


class ValidationError(Exception):
    """Raised when message validation fails."""
    pass


class MessageValidator:
    """Validates message content and structure."""
    
    # Message type registry
    MESSAGE_TYPES = {
        "user": UserMessage,
        "assistant": AssistantMessage,
        "system": SystemMessage,
        "tool": ToolMessage,
        "error": ErrorMessage,
    }
    
    # Content validation patterns
    CONTENT_PATTERNS = {
        "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        "phone": r'^[\+]?[\d\s\-\(\)]+$',
        "url": r'https?://[^\s]+',
        "json": r'^\{.*\}$|\[.*\]$',
    }
    
    def __init__(self):
        """Initialize message validator."""
        self.custom_validators: Dict[str, List[callable]] = {}
        self.content_filters: List[callable] = []
        
    def add_custom_validator(self, message_type: str, validator: callable) -> None:
        """Add custom validator for specific message type.
        
        Args:
            message_type: Message type to validate
            validator: Function that takes message and returns bool or raises ValidationError
        """
        if message_type not in self.custom_validators:
            self.custom_validators[message_type] = []
        self.custom_validators[message_type].append(validator)
    
    def add_content_filter(self, filter_func: callable) -> None:
        """Add content filter for all messages.
        
        Args:
            filter_func: Function that takes content and returns filtered content or raises ValidationError
        """
        self.content_filters.append(filter_func)
    
    def validate_message(self, message: Union[Message, Dict[str, Any]]) -> Message:
        """Validate a message object or dictionary.
        
        Args:
            message: Message object or dictionary to validate
            
        Returns:
            Validated message object
            
        Raises:
            ValidationError: If validation fails
        """
        if isinstance(message, dict):
            message = self._create_message_from_dict(message)
        
        # Basic validation
        self._validate_basic_message(message)
        
        # Type-specific validation
        self._validate_message_type(message)
        
        # Apply content filters
        for filter_func in self.content_filters:
            try:
                message.content = filter_func(message.content)
            except Exception as e:
                raise ValidationError(f"Content filter failed: {str(e)}")
        
        return message
    
    def validate_response(self, response: Union[AssistantResponse, Dict[str, Any]]) -> AssistantResponse:
        """Validate assistant response.
        
        Args:
            response: Response object or dictionary to validate
            
        Returns:
            Validated response object
        """
        if isinstance(response, dict):
            response = AssistantResponse.from_dict(response)
        
        # Validate content
        if not hasattr(response, 'content') or not response.content:
            raise ValidationError("Response content is required")
        
        # Validate confidence
        if not isinstance(response.confidence, (int, float)) or not 0.0 <= response.confidence <= 1.0:
            raise ValidationError("Confidence must be a number between 0.0 and 1.0")
        
        # Validate execution time
        if response.execution_time_ms < 0:
            raise ValidationError("Execution time cannot be negative")
        
        return response
    
    def _validate_basic_message(self, message: Message) -> None:
        """Validate basic message requirements."""
        if not hasattr(message, 'content') or not message.content:
            raise ValidationError("Message content is required")
        
        if not hasattr(message, 'message_type') or not message.message_type:
            raise ValidationError("Message type is required")
        
        if message.message_type not in self.MESSAGE_TYPES:
            raise ValidationError(f"Unknown message type: {message.message_type}")
        
        if not hasattr(message, 'timestamp') or not isinstance(message.timestamp, datetime):
            raise ValidationError("Message timestamp is required")
        
        if not hasattr(message, 'message_id'):
            raise ValidationError("Message ID is required")
    
    def _validate_message_type(self, message: Message) -> None:
        """Validate message based on its type."""
        message_type = message.message_type
        
        if message_type == "user":
            self._validate_user_message(message)
        elif message_type == "assistant":
            self._validate_assistant_message(message)
        elif message_type == "system":
            self._validate_system_message(message)
        elif message_type == "tool":
            self._validate_tool_message(message)
        elif message_type == "error":
            self._validate_error_message(message)
        
        # Apply custom validators
        for validator in self.custom_validators.get(message_type, []):
            try:
                if not validator(message):
                    raise ValidationError(f"Custom validation failed for {message_type} message")
            except ValidationError:
                raise
            except Exception as e:
                raise ValidationError(f"Custom validation error: {str(e)}")
    
    def _validate_user_message(self, message: UserMessage) -> None:
        """Validate user message specific requirements."""
        # Check for potentially harmful content
        if self._contains_harmful_content(message.content):
            raise ValidationError("Message contains potentially harmful content")
        
        # Validate user ID if present
        user_id = message.get_metadata("user_id")
        if user_id and not isinstance(user_id, str):
            raise ValidationError("User ID must be a string")
    
    def _validate_assistant_message(self, message: AssistantMessage) -> None:
        """Validate assistant message specific requirements."""
        if not isinstance(message.confidence, (int, float)) or not 0.0 <= message.confidence <= 1.0:
            raise ValidationError("Confidence must be a number between 0.0 and 1.0")
        
        # Validate tool calls if present
        if message.tool_calls:
            for tool_call in message.tool_calls:
                if not isinstance(tool_call, dict) or "name" not in tool_call:
                    raise ValidationError("Tool calls must be dictionaries with 'name' field")
    
    def _validate_system_message(self, message: SystemMessage) -> None:
        """Validate system message specific requirements."""
        valid_levels = ["debug", "info", "warning", "error", "critical"]
        if message.level not in valid_levels:
            raise ValidationError(f"System message level must be one of: {valid_levels}")
    
    def _validate_tool_message(self, message: ToolMessage) -> None:
        """Validate tool message specific requirements."""
        if not message.tool_name:
            raise ValidationError("Tool name is required")
        
        if not isinstance(message.tool_args, dict):
            raise ValidationError("Tool arguments must be a dictionary")
        
        if message.execution_time_ms < 0:
            raise ValidationError("Execution time cannot be negative")
    
    def _validate_error_message(self, message: ErrorMessage) -> None:
        """Validate error message specific requirements."""
        # Error messages are allowed to have specific fields
        pass
    
    def _contains_harmful_content(self, content: str) -> bool:
        """Check for potentially harmful content patterns."""
        harmful_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'expression\s*\(',
            r'@import',
            r'url\s*\(',
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _create_message_from_dict(self, data: Dict[str, Any]) -> Message:
        """Create message object from dictionary."""
        message_type = data.get("message_type")
        if not message_type:
            raise ValidationError("Message type is required in dictionary")
        
        if message_type not in self.MESSAGE_TYPES:
            raise ValidationError(f"Unknown message type: {message_type}")
        
        message_class = self.MESSAGE_TYPES[message_type]
        return message_class.from_dict(data)
    
    def validate_content_pattern(self, content: str, pattern_name: str) -> bool:
        """Validate content against specific pattern.
        
        Args:
            content: Content to validate
            pattern_name: Pattern name to check against
            
        Returns:
            True if content matches pattern
        """
        if pattern_name not in self.CONTENT_PATTERNS:
            raise ValueError(f"Unknown pattern: {pattern_name}")
        
        pattern = self.CONTENT_PATTERNS[pattern_name]
        return bool(re.match(pattern, content, re.IGNORECASE))


class MessageSerializer:
    """Handles message serialization and deserialization."""
    
    def __init__(self, validator: Optional[MessageValidator] = None):
        """Initialize message serializer.
        
        Args:
            validator: Optional message validator
        """
        self.validator = validator or MessageValidator()
        self.serializer_config = {
            "indent": 2,
            "ensure_ascii": False,
            "sort_keys": False,
        }
    
    def serialize_message(self, message: Message, format: str = "json") -> str:
        """Serialize message to string format.
        
        Args:
            message: Message to serialize
            format: Serialization format ('json', 'compact')
            
        Returns:
            Serialized message string
        """
        # Validate before serialization
        validated_message = self.validator.validate_message(message)
        
        if format == "json":
            return validated_message.to_json()
        elif format == "compact":
            return json.dumps(validated_message.to_dict(), separators=(',', ':'), default=str)
        else:
            raise ValueError(f"Unsupported serialization format: {format}")
    
    def serialize_response(self, response: AssistantResponse, format: str = "json") -> str:
        """Serialize assistant response to string format.
        
        Args:
            response: Response to serialize
            format: Serialization format ('json', 'compact')
            
        Returns:
            Serialized response string
        """
        # Validate before serialization
        validated_response = self.validator.validate_response(response)
        
        if format == "json":
            return validated_response.to_json()
        elif format == "compact":
            return json.dumps(validated_response.to_dict(), separators=(',', ':'), default=str)
        else:
            raise ValueError(f"Unsupported serialization format: {format}")
    
    def deserialize_message(self, data: Union[str, Dict[str, Any]]) -> Message:
        """Deserialize message from string or dictionary.
        
        Args:
            data: Message data (JSON string or dictionary)
            
        Returns:
            Deserialized and validated message
        """
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON format: {str(e)}")
        
        return self.validator.validate_message(data)
    
    def deserialize_response(self, data: Union[str, Dict[str, Any]]) -> AssistantResponse:
        """Deserialize response from string or dictionary.
        
        Args:
            data: Response data (JSON string or dictionary)
            
        Returns:
            Deserialized and validated response
        """
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON format: {str(e)}")
        
        return self.validator.validate_response(data)
    
    def serialize_conversation(
        self, 
        messages: List[Message], 
        format: str = "json"
    ) -> str:
        """Serialize conversation history.
        
        Args:
            messages: List of messages
            format: Serialization format
            
        Returns:
            Serialized conversation
        """
        validated_messages = [self.validator.validate_message(msg) for msg in messages]
        conversation_data = [msg.to_dict() for msg in validated_messages]
        
        if format == "json":
            return json.dumps(conversation_data, **self.serializer_config, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def deserialize_conversation(self, data: Union[str, List[Dict[str, Any]]]) -> List[Message]:
        """Deserialize conversation history.
        
        Args:
            data: Conversation data (JSON string array or list of dictionaries)
            
        Returns:
            List of validated messages
        """
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON format: {str(e)}")
        
        if not isinstance(data, list):
            raise ValidationError("Conversation must be a list of messages")
        
        messages = []
        for msg_data in data:
            try:
                message = self.validator.validate_message(msg_data)
                messages.append(message)
            except ValidationError as e:
                raise ValidationError(f"Invalid message in conversation: {str(e)}")
        
        return messages


# Global validator and serializer instances
default_validator = MessageValidator()
default_serializer = MessageSerializer(default_validator)


def validate_message(message: Union[Message, Dict[str, Any]]) -> Message:
    """Validate message using default validator."""
    return default_validator.validate_message(message)


def validate_response(response: Union[AssistantResponse, Dict[str, Any]]) -> AssistantResponse:
    """Validate response using default validator."""
    return default_validator.validate_response(response)


def serialize_message(message: Message, format: str = "json") -> str:
    """Serialize message using default serializer."""
    return default_serializer.serialize_message(message, format)


def serialize_response(response: AssistantResponse, format: str = "json") -> str:
    """Serialize response using default serializer."""
    return default_serializer.serialize_response(response, format)


def deserialize_message(data: Union[str, Dict[str, Any]]) -> Message:
    """Deserialize message using default serializer."""
    return default_serializer.deserialize_message(data)


def deserialize_response(data: Union[str, Dict[str, Any]]) -> AssistantResponse:
    """Deserialize response using default serializer."""
    return default_serializer.deserialize_response(data)