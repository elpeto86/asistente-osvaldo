"""Pytest configuration and fixtures for the assistant framework."""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Any, Dict, Generator, Optional
import pytest

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def test_config_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test configurations."""
    temp_dir = Path(tempfile.mkdtemp(prefix="assistant_test_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_config(test_config_dir: Path) -> Dict[str, Any]:
    """Provide a mock configuration for tests."""
    env_file = test_config_dir / ".env"
    env_file.write_text("""
# Test configuration
ASSISTANT_NAME=test-assistant
ASSISTANT_VERSION=0.1.0
LOG_LEVEL=DEBUG
API_BASE_URL=https://api.test.com
API_KEY=test-api-key-123
DATABASE_URL=sqlite:///test.db
    """)
    
    return {
        "assistant": {
            "name": "test-assistant",
            "version": "0.1.0",
            "description": "Test assistant instance"
        },
        "logging": {
            "level": "DEBUG",
            "format": "json",
            "handlers": ["console"]
        },
        "api": {
            "base_url": "https://api.test.com",
            "key": "test-api-key-123",
            "timeout": 30
        },
        "database": {
            "url": "sqlite:///test.db",
            "pool_size": 5
        }
    }


@pytest.fixture
def mock_assistant(mock_config: Dict[str, Any]):
    """Provide a mock assistant instance for testing."""
    from assistant.core.base_assistant import BaseAssistant
    from assistant.interfaces.messages import AssistantMessage, UserMessage
    from assistant.interfaces.responses import AssistantResponse
    import asyncio
    
    class MockAssistant(BaseAssistant):
        def __init__(self, config: Dict[str, Any]):
            self.config = config
            self.is_configured = False
            self.messages = []
            
        async def process_input(self, message: UserMessage) -> AssistantResponse:
            """Mock processing that echoes the input."""
            self.messages.append(message)
            response = AssistantResponse(
                content=f"Mock response to: {message.content}",
                metadata={"model": "mock", "tokens": 10},
                confidence=0.95
            )
            return response
            
        async def configure(self) -> None:
            """Mock configuration."""
            self.is_configured = True
            
        async def cleanup(self) -> None:
            """Mock cleanup."""
            self.messages.clear()
    
    return MockAssistant(mock_config)


@pytest.fixture
def sample_messages():
    """Provide sample messages for testing."""
    from assistant.interfaces.messages import UserMessage, AssistantMessage, SystemMessage
    
    return {
        "user": UserMessage(content="Hello, how are you?", user_id="test_user"),
        "assistant": AssistantMessage(content="I'm doing well, thank you!", metadata={"model": "test"}),
        "system": SystemMessage(content="You are a helpful assistant.")
    }


@pytest.fixture
def sample_responses():
    """Provide sample responses for testing."""
    from assistant.interfaces.responses import AssistantResponse
    
    return {
        "success": AssistantResponse(
            content="This is a successful response",
            metadata={"model": "test-model", "tokens": 15},
            confidence=0.95
        ),
        "low_confidence": AssistantResponse(
            content="I'm not sure about this",
            metadata={"model": "test-model", "tokens": 8},
            confidence=0.45
        )
    }


@pytest.fixture
def temp_directory() -> Generator[Path, None, None]:
    """Create a temporary directory for file operations."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_ai_response():
    """Fixture for providing predefined AI responses."""
    def _create_response(content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": len(content.split()),
                "total_tokens": 10 + len(content.split())
            },
            "model": "gpt-3.5-turbo-test",
            **(metadata or {})
        }
    
    return _create_response


@pytest.fixture
def mock_external_service(monkeypatch):
    """Mock external service calls."""
    responses = []
    
    def mock_call(*args, **kwargs):
        if responses:
            return responses.pop(0)
        return {"status": "ok", "data": {"result": "mock"}}
    
    def set_response(response):
        responses.append(response)
    
    monkeypatch.setattr("requests.post", mock_call)
    monkeypatch.setattr("requests.get", mock_call)
    
    return type("MockService", (), {"set_response": set_response})()


@pytest.fixture
def test_logger():
    """Provide a test logger instance."""
    import logging
    from assistant.core.logger import get_logger
    
    return get_logger("test")


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment variables before and after tests."""
    # Remove potential test environment variables
    original_env = {}
    test_vars = [
        "ASSISTANT_API_KEY", "DATABASE_URL", "LOG_LEVEL",
        "ASSISTANT_NAME", "ASSISTANT_VERSION", "CONFIG_FILE"
    ]
    
    for var in test_vars:
        if var in os.environ:
            original_env[var] = os.environ[var]
            del os.environ[var]
    
    yield
    
    # Restore environment
    os.environ.update(original_env)


# Custom markers for better test organization
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "api: mark test as API test")
    config.addinivalue_line("markers", "external: mark test that calls external services")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on file location
        if "integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add markers based on function names
        if "api" in item.nodeid.lower():
            item.add_marker(pytest.mark.api)
        elif "external" in item.nodeid.lower():
            item.add_marker(pytest.mark.external)