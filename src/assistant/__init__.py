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
    from .interfaces.message import UserMessage, AssistantMessage, SystemMessage
    from .interfaces.responses import AssistantResponse
    from .core.config import Config
    
    __all__ = [
        "BaseAssistant",
        "UserMessage", 
        "AssistantMessage",
        "SystemMessage",
        "AssistantResponse",
        "Config",
    ]
except ImportError:
    # Modules not yet created during setup
    __all__ = []
    pass