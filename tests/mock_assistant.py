"""Test utilities and helper functions for the assistant framework."""

import asyncio
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json

from assistant.interfaces.messages import UserMessage, AssistantMessage, SystemMessage
from assistant.interfaces.responses import AssistantResponse


class MockAssistant:
    """A mock assistant implementation for testing purposes."""
    
    def __init__(self, responses: Optional[List[str]] = None, fail_on_process: bool = False):
        self.responses = responses or ["Mock response", "Another mock response"]
        self.fail_on_process = fail_on_process
        self.processed_messages: List[UserMessage] = []
        self.is_configured = False
        self.cleanups = 0
    
    async def process_input(self, message: UserMessage) -> AssistantResponse:
        """Mock processing that returns predefined responses or raises error."""
        self.processed_messages.append(message)
        
        if self.fail_on_process:
            raise RuntimeError("Mock assistant configured to fail")
        
        response_text = self.responses[len(self.processed_messages) - 1] if len(self.processed_messages) <= len(self.responses) else "Default mock response"
        
        return AssistantResponse(
            content=response_text,
            metadata={"model": "mock", "tokens": 10},
            confidence=0.95
        )
    
    async def configure(self) -> None:
        """Mock configuration."""
        await asyncio.sleep(0.01)  # Simulate async work
        self.is_configured = True
    
    async def cleanup(self) -> None:
        """Mock cleanup."""
        await asyncio.sleep(0.01)  # Simulate async work
        self.cleanups += 1


class TestMessageFactory:
    """Factory for creating test messages."""
    
    @staticmethod
    def user_message(content: str, user_id: str = "test_user", **kwargs) -> UserMessage:
        """Create a user message for testing."""
        return UserMessage(content=content, user_id=user_id, **kwargs)
    
    @staticmethod
    def assistant_message(content: str, metadata: Optional[Dict[str, Any]] = None, **kwargs) -> AssistantMessage:
        """Create an assistant message for testing."""
        if metadata is None:
            metadata = {"model": "test-model"}
        return AssistantMessage(content=content, metadata=metadata, **kwargs)
    
    @staticmethod
    def system_message(content: str, **kwargs) -> SystemMessage:
        """Create a system message for testing."""
        return SystemMessage(content=content, **kwargs)
    
    @staticmethod
    def conversation() -> List[Union[UserMessage, AssistantMessage, SystemMessage]]:
        """Create a sample conversation for testing."""
        return [
            TestMessageFactory.system_message("You are a helpful assistant."),
            TestMessageFactory.user_message("Hello, how are you?", user_id="user1"),
            TestMessageFactory.assistant_message("I'm doing well, thank you!"),
            TestMessageFactory.user_message("What can you do?", user_id="user1"),
        ]


class TestResponseFactory:
    """Factory for creating test responses."""
    
    @staticmethod
    def success_response(
        content: str = "Success response",
        confidence: float = 0.95,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AssistantResponse:
        """Create a successful response."""
        if metadata is None:
            metadata = {"model": "test-model", "tokens": 10}
        return AssistantResponse(
            content=content,
            metadata=metadata,
            confidence=confidence
        )
    
    @staticmethod
    def low_confidence_response(content: str = "I'm not sure") -> AssistantResponse:
        """Create a response with low confidence."""
        return AssistantResponse(
            content=content,
            metadata={"model": "test-model", "tokens": 8},
            confidence=0.45
        )
    
    @staticmethod
    def error_response(content: str = "An error occurred") -> AssistantResponse:
        """Create an error response."""
        return AssistantResponse(
            content=content,
            metadata={"model": "test-model", "error": True},
            confidence=0.10
        )
    
    @staticmethod
    def empty_response() -> AssistantResponse:
        """Create an empty response."""
        return AssistantResponse(
            content="",
            metadata={"model": "test-model", "tokens": 0},
            confidence=0.0
        )


class TestAssertionHelpers:
    """Helper functions for asserting test conditions."""
    
    @staticmethod
    def assert_valid_response(response: AssistantResponse, should_have_content: bool = True):
        """Assert that a response is valid."""
        assert isinstance(response, AssistantResponse)
        assert isinstance(response.content, str)
        assert isinstance(response.confidence, float)
        assert 0.0 <= response.confidence <= 1.0
        assert isinstance(response.metadata, dict)
        
        if should_have_content:
            assert len(response.content) > 0
    
    @staticmethod
    def assert_valid_message(message, message_type: type):
        """Assert that a message is of the correct type and valid."""
        assert isinstance(message, message_type)
        assert isinstance(message.content, str)
        assert len(message.content) > 0
        
        if isinstance(message, UserMessage):
            assert isinstance(message.user_id, str)
            assert len(message.user_id) > 0
    
    @staticmethod
    def assert_conversation_flow(messages: List[Union[UserMessage, AssistantMessage, SystemMessage]]):
        """Assert that a conversation has proper flow."""
        if messages:
            # First message could be system or user
            assert isinstance(messages[0], (SystemMessage, UserMessage))
            
            # Check alternating pattern (except for system messages)
            last_user = False
            last_assistant = False
            system_seen = False
            
            for msg in messages:
                if isinstance(msg, SystemMessage):
                    system_seen = True
                    continue
                
                if isinstance(msg, UserMessage):
                    assert not last_user, f"Two user messages in a row: {msg.content[:50]}"
                    last_user = True
                    last_assistant = False
                elif isinstance(msg, AssistantMessage):
                    assert not last_assistant, f"Two assistant messages in a row: {msg.content[:50]}"
                    last_assistant = True
                    last_user = False


class AsyncTestHelper:
    """Helper for running async tests."""
    
    @staticmethod
    def run_async(coro):
        """Run async coroutine in sync context."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    
    @staticmethod
    async def gather_with_errors(*tasks):
        """Gather tasks and collect any exceptions."""
        results = []
        errors = []
        
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        return results, errors


class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def generate_config_data() -> Dict[str, Any]:
        """Generate test configuration data."""
        return {
            "assistant": {
                "name": "test-assistant",
                "version": "0.1.0",
                "description": "Test assistant"
            },
            "logging": {
                "level": "DEBUG",
                "format": "simple",
                "handlers": ["console"]
            },
            "api": {
                "base_url": "https://api.test.com",
                "key": "test-key",
                "timeout": 30
            }
        }
    
    @staticmethod
    def generate_batch_messages(count: int) -> List[UserMessage]:
        """Generate multiple user messages for batch testing."""
        messages = []
        for i in range(count):
            messages.append(TestMessageFactory.user_message(
                content=f"Test message {i+1}",
                user_id=f"user{i%5+1}"  # Cycle through 5 users
            ))
        return messages
    
    @staticmethod
    def save_test_data(data: Any, path: Union[str, Path]):
        """Save test data to a file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_test_data(path: Union[str, Path]) -> Any:
        """Load test data from a file."""
        path = Path(path)
        
        with open(path, 'r') as f:
            return json.load(f)


# Utility functions for common test scenarios
async def simulate_api_call(delay: float = 0.1, should_fail: bool = False) -> Dict[str, Any]:
    """Simulate an API call with optional delay and failure."""
    await asyncio.sleep(delay)
    
    if should_fail:
        raise RuntimeError("Simulated API failure")
    
    return {"status": "success", "data": {"result": "test data"}}


def create_test_environment(env_vars: Dict[str, str]) -> Dict[str, str]:
    """Create test environment variables."""
    import os
    original_env = {}
    
    for key, value in env_vars.items():
        if key in os.environ:
            original_env[key] = os.environ[key]
        os.environ[key] = value
    
    return original_env


def restore_environment(original_env: Dict[str, str]):
    """Restore original environment variables."""
    import os
    
    # Remove test variables
    test_keys = [
        "ASSISTANT_API_KEY", "DATABASE_URL", "LOG_LEVEL",
        "ASSISTANT_NAME", "ASSISTANT_VERSION"
    ]
    
    for key in test_keys:
        if key in os.environ and key not in original_env:
            del os.environ[key]
    
    # Restore original values
    os.environ.update(original_env)