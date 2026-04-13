"""Test utilities for creating messages and responses."""

from typing import Any, Dict, List, Optional
import json
from datetime import datetime

from assistant.interfaces.messages import UserMessage, AssistantMessage, SystemMessage
from assistant.interfaces.responses import AssistantResponse


class MessageBuilder:
    """Builder pattern for creating test messages."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset builder to default state."""
        self._content = ""
        self._user_id = "test_user"
        self._metadata = {}
        self._message_type = "user"
        return self
    
    def content(self, content: str):
        """Set message content."""
        self._content = content
        return self
    
    def user_id(self, user_id: str):
        """Set user ID (for user messages)."""
        self._user_id = user_id
        return self
    
    def metadata(self, metadata: Dict[str, Any]):
        """Set metadata (for assistant messages)."""
        self._metadata = metadata
        return self
    
    def user(self) -> UserMessage:
        """Create a user message."""
        self._message_type = "user"
        return self.build()
    
    def assistant(self) -> AssistantMessage:
        """Create an assistant message."""
        self._message_type = "assistant"
        return self.build()
    
    def system(self) -> SystemMessage:
        """Create a system message."""
        self._message_type = "system"
        return self.build()
    
    def build(self):
        """Build the message based on current type."""
        if self._message_type == "user":
            return UserMessage(
                content=self._content or "Test user message",
                user_id=self._user_id,
                metadata=self._metadata.copy()
            )
        elif self._message_type == "assistant":
            return AssistantMessage(
                content=self._content or "Test assistant message",
                metadata={"model": "test-model", "timestamp": datetime.now().isoformat(), **self._metadata}
            )
        elif self._message_type == "system":
            return SystemMessage(
                content=self._content or "You are a helpful assistant."
            )
        else:
            raise ValueError(f"Unknown message type: {self._message_type}")


class ResponseBuilder:
    """Builder pattern for creating test responses."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset builder to default state."""
        self._content = ""
        self._confidence = 0.95
        self._metadata = {}
        return self
    
    def content(self, content: str):
        """Set response content."""
        self._content = content
        return self
    
    def confidence(self, confidence: float):
        """Set confidence score (0.0 to 1.0)."""
        self._confidence = max(0.0, min(1.0, confidence))
        return self
    
    def metadata(self, metadata: Dict[str, Any]):
        """Set metadata."""
        self._metadata = metadata
        return self
    
    def tokens(self, tokens: int):
        """Set token count in metadata."""
        self._metadata["tokens"] = tokens
        return self
    
    def model(self, model: str):
        """Set model name in metadata."""
        self._metadata["model"] = model
        return self
    
    def error(self, error: bool = True):
        """Mark as error response."""
        self._metadata["error"] = error
        return self
    
    def build(self) -> AssistantResponse:
        """Build the response."""
        return AssistantResponse(
            content=self._content or "Test response",
            metadata={
                "model": "test-model",
                "tokens": 10,
                "timestamp": datetime.now().isoformat(),
                **self._metadata
            },
            confidence=self._confidence
        )


class ConversationScenario:
    """Pre-defined conversation scenarios for testing."""
    
    @staticmethod
    def simple_qa() -> List:
        """Simple question-answer conversation."""
        builder = MessageBuilder()
        return [
            builder.reset().content("What is the capital of France?").user(),
            builder.reset().content("The capital of France is Paris.").assistant()
        ]
    
    @staticmethod
    def multi_turn() -> List:
        """Multi-turn conversation with follow-up questions."""
        builder = MessageBuilder()
        return [
            builder.reset().content("Explain photosynthesis.").user(),
            builder.reset().content("Photosynthesis is the process by which plants convert light, water, and carbon dioxide into energy.").assistant(),
            builder.reset().content("What are the key components needed?").user(),
            builder.reset().content("The key components are: sunlight, water (H2O), carbon dioxide (CO2), and chlorophyll in the plant leaves.").assistant(),
            builder.reset().content("Thank you for the explanation!").user()
        ]
    
    @staticmethod
    def error_recovery() -> List:
        """Conversation with error handling."""
        builder = MessageBuilder()
        return [
            builder.reset().content("Process this complex data.").user(),
            builder.reset().content("I'm having trouble processing that request. Can you provide the data in a simpler format?").assistant(),
            builder.reset().content("Here's the simplified data: [1, 2, 3]").user(),
            builder.reset().content("Processed successfully: The sum is 6.").assistant()
        ]
    
    @staticmethod
    def system_prompt() -> List:
        """Conversation with system prompt."""
        builder = MessageBuilder()
        return [
            builder.reset().content("You are a Python programming expert. Always provide code examples.").system(),
            builder.reset().content("How do I create a list comprehension?").user(),
            builder.reset().content("Here's how to create a list comprehension:\n\n```python\nsquares = [x**2 for x in range(10)]\n```\n\nThis creates a list of squares from 0 to 9.").assistant()
        ]


class ResponseScenarios:
    """Pre-defined response scenarios for testing."""
    
    @staticmethod
    def success_scenarios() -> Dict[str, AssistantResponse]:
        """Various successful response scenarios."""
        builder = ResponseBuilder()
        return {
            "simple": builder.reset().content("Simple response").build(),
            "detailed": builder.reset().content("Detailed response with more information").tokens(25).build(),
            "high_confidence": builder.reset().content("High confidence answer").confidence(0.98).build(),
            "low_confidence": builder.reset().content("Not sure about this").confidence(0.45).model("gpt-3.5-turbo").build(),
        }
    
    @staticmethod
    def error_scenarios() -> Dict[str, AssistantResponse]:
        """Various error response scenarios."""
        builder = ResponseBuilder()
        return {
            "network_error": builder.reset().content("Network connection failed").error().confidence(0.1).build(),
            "invalid_input": builder.reset().content("Invalid input format").error().confidence(0.2).build(),
            "timeout": builder.reset().content("Request timed out").error().confidence(0.0).build(),
        }
    
    @staticmethod
    def edge_cases() -> Dict[str, AssistantResponse]:
        """Edge case responses."""
        builder = ResponseBuilder()
        return {
            "empty": builder.reset().content("").confidence(0.0).build(),
            "very_long": builder.reset().content("A" * 1000).tokens(1000).build(),
            "unicode": builder.reset().content("Response with emojis: 🚀🎉ℹ️").build(),
            "json_content": builder.reset().content(json.dumps({"key": "value"})).build()
        }


class TestGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def random_messages(count: int, include_system: bool = False) -> List:
        """Generate random messages for testing."""
        import random
        
        messages = []
        
        if include_system:
            messages.append(MessageBuilder().reset().system().build())
        
        for i in range(count):
            is_user = i % 2 == 0
            builder = MessageBuilder().reset()
            
            if is_user:
                builder.content(f"Random message {i+1}")
                messages.append(builder.user_id(f"user{i%5+1}").user())
            else:
                builder.content(f"Random response {i+1}")
                messages.append(builder.assistant())
        
        return messages
    
    @staticmethod
    def stress_test_data(size: int = 100) -> Dict[str, Any]:
        """Generate data for stress testing."""
        return {
            "messages": TestGenerator.random_messages(size),
            "batch_size": 10,
            "concurrent_requests": 5,
            "total_pages": size // 10 + 1
        }
    
    @staticmethod
    def performance_metrics() -> Dict[str, Any]:
        """Generate performance test metrics."""
        return {
            "latency": {
                "p50": 150,  # milliseconds
                "p95": 500,
                "p99": 1000
            },
            "throughput": {
                "requests_per_second": 100,
                "messages_per_second": 250
            },
            "resource_usage": {
                "memory_mb": 128,
                "cpu_percent": 25
            }
        }


class ValidationHelpers:
    """Helpers for validating test data."""
    
    @staticmethod
    def assert_message_sequence(messages: List, expected_types: List[str]):
        """Assert that messages follow expected type sequence."""
        assert len(messages) == len(expected_types), f"Message count mismatch: {len(messages)} != {len(expected_types)}"
        
        for i, (message, expected_type) in enumerate(zip(messages, expected_types)):
            if expected_type == "user":
                assert isinstance(message, UserMessage), f"Message {i} should be UserMessage"
            elif expected_type == "assistant":
                assert isinstance(message, AssistantMessage), f"Message {i} should be AssistantMessage"
            elif expected_type == "system":
                assert isinstance(message, SystemMessage), f"Message {i} should be SystemMessage"
    
    @staticmethod
    def validate_response_format(response: AssistantResponse):
        """Validate response format and content."""
        assert isinstance(response, AssistantResponse)
        assert isinstance(response.content, str)
        assert isinstance(response.confidence, float)
        assert 0.0 <= response.confidence <= 1.0
        assert isinstance(response.metadata, dict)
        assert "timestamp" in response.metadata
    
    @staticmethod
    def count_message_types(conversation: List) -> Dict[str, int]:
        """Count message types in conversation."""
        counts = {
            "user": 0,
            "assistant": 0,
            "system": 0
        }
        
        for message in conversation:
            if isinstance(message, UserMessage):
                counts["user"] += 1
            elif isinstance(message, AssistantMessage):
                counts["assistant"] += 1
            elif isinstance(message, SystemMessage):
                counts["system"] += 1
        
        return counts


# Quick access factory functions
def create_user_message(content: str, user_id: str = "test_user") -> UserMessage:
    """Quickly create a user message."""
    return MessageBuilder().reset().content(content).user_id(user_id).user()


def create_assistant_message(content: str, metadata: Optional[Dict[str, Any]] = None) -> AssistantMessage:
    """Quickly create an assistant message."""
    return MessageBuilder().reset().content(content).metadata(metadata or {}).assistant()


def create_system_message(content: str = "You are a helpful assistant.") -> SystemMessage:
    """Quickly create a system message."""
    return MessageBuilder().reset().content(content).system()


def create_response(content: str, confidence: float = 0.95) -> AssistantResponse:
    """Quickly create a response."""
    return ResponseBuilder().reset().content(content).confidence(confidence).build()