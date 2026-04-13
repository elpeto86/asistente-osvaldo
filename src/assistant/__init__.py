"""
Osvaldo AI Assistant - A modular Python assistant framework.

This package provides a standardized foundation for building AI assistants
with configuration management, logging, testing, and extensible architecture.

Features:
- Modular architecture with clear separation of concerns
- Type-safe configuration management with Pydantic
- Structured logging with multiple handlers
- Comprehensive testing framework setup
- Plugin system for extensibility
"""

__version__ = "0.1.0"
__author__ = "Asistente Osvaldo Team"
__email__ = "osvaldo@example.com"
__description__ = "A modular Python assistant framework for building intelligent assistants"

# Import will be updated as modules are created
try:
    from .core.assistant import BaseAssistant
    from .interfaces.message import UserMessage, AssistantMessage, SystemMessage, Message
    from .interfaces.responses import AssistantResponse
    from .core.config import Config
    from .interfaces.validation import (
        validate_message, 
        validate_response, 
        serialize_message, 
        serialize_response
    )
    
    __all__ = [
        "BaseAssistant",
        "UserMessage", 
        "AssistantMessage",
        "SystemMessage",
        "Message",
        "AssistantResponse",
        "Config",
        "validate_message",
        "validate_response", 
        "serialize_message",
        "serialize_response",
    ]
except ImportError:
    # Modules not yet created during setup
    __all__ = [
        "__version__",
        "__author__",
        "__email__",
        "__description__",
    ]
    pass