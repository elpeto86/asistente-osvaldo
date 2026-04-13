"""
Testing de Componentes con el Asistente Osvaldo

Este ejemplo muestra cómo probar los componentes del framework
utilizando pytest con fixtures y utilidades personalizadas.
"""

import asyncio
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Agregar el directorio src al path para importar el módulo
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from assistant import BaseAssistant, UserMessage, AssistantMessage, Config
from assistant.interfaces.validation import validate_message, validate_response
from assistant.utils import get_logger


# Implementación de asistente para testing
class TestAssistant(BaseAssistant):
    """Asistente simple para ejemplos de testing."""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.processed_messages = []
        self.logger = get_logger("test_assistant")
    
    async def process_input(self, message: UserMessage) -> AssistantMessage:
        """Procesa mensajes registrando cada llamada."""
        self.processed_messages.append(message)
        
        response_content = f"Test response for: {message.content}"
        
        return AssistantMessage(
            content=response_content,
            confidence=0.85
        )
    
    def configure(self, config: Config) -> None:
        self.logger.info("TestAssistant configured")
    
    def cleanup(self) -> None:
        self.processed_messages.clear()


# Fixtures de ejemplo
@pytest.fixture
def sample_config():
    """Crea una configuración de prueba."""
    return Config(
        assistant_name="TestAssistant",
        log_level="DEBUG"
    )


@pytest.fixture
def test_assistant(sample_config):
    """Crea una instancia de TestAssistant para testing."""
    assistant = TestAssistant(sample_config)
    assistant.configure(sample_config)
    yield assistant
    assistant.cleanup()


@pytest.fixture
def sample_messages():
    """Proporciona mensajes de prueba."""
    return [
        UserMessage(content="Test message 1"),
        UserMessage(content="Test message 2"),
        UserMessage(content="Another test message")
    ]


# Ejemplos de tests
def test_assistant_initialization(sample_config):
    """Test de inicialización del asistente."""
    assistant = TestAssistant(sample_config)
    
    assert assistant.config == sample_config
    assert len(assistant.processed_messages) == 0
    
    assistant.cleanup()


async def test_message_processing(test_assistant, sample_messages):
    """Test de procesamiento de mensajes."""
    # Procesar mensajes
    for message in sample_messages:
        response = await test_assistant.process_input(message)
        
        # Verificar respuesta
        assert isinstance(response, AssistantMessage)
        assert "Test response for:" in response.content
        assert response.confidence == 0.85
    
    # Verificar que todos los mensajes fueron registrados
    assert len(test_assistant.processed_messages) == 3
    assert test_assistant.processed_messages == sample_messages


def test_message_validation():
    """Test de validación de mensajes."""
    # Mensaje válido
    valid_message = UserMessage(content="Valid message")
    assert validate_message(valid_message) is True
    
    # Mensaje inválido (contenido vacío)
    try:
        invalid_message = UserMessage(content="")
        validate_message(invalid_message)
        assert False, "Debería haber fallado la validación"
    except ValueError as e:
        assert "empty content" in str(e).lower()


def test_response_validation():
    """Test de validación de respuestas."""
    # Respuesta válida
    valid_response = AssistantResponse(
        content="Valid response",
        confidence=0.9,
        metadata={"source": "test"}
    )
    assert validate_response(valid_response) is True
    
    # Respuesta inválida (confianza fuera de rango)
    try:
        invalid_response = AssistantResponse(
            content="Invalid response",
            confidence=1.5  # Fuera del rango 0-1
        )
        validate_response(invalid_response)
        assert False, "Debería haber fallado la validación"
    except ValueError as e:
        assert "confidence" in str(e).lower()


# Test con mocks
def test_assistant_with_mock():
    """Test de asistente utilizando mocks."""
    # Crear mock de configuración
    mock_config = Mock(spec=Config)
    mock_config.assistant_name = "MockAssistant"
    mock_config.log_level = "INFO"
    
    assistant = TestAssistant(mock_config)
    
    # Usar AsyncMock para el método async
    assistant.process_input = AsyncMock(return_value=AssistantResponse(
        content="Mock response",
        confidence=0.95
    ))
    
    # Ejecutar el test asíncrono
    async def run_test():
        message = UserMessage(content="Test message")
        response = await assistant.process_input(message)
        
        assert response.content == "Mock response"
        assert response.confidence == 0.95
        
        # Verificar que el mock fue llamado
        assistant.process_input.assert_called_once_with(message)
    
    asyncio.run(run_test()


# Test de configuración
def test_config_management():
    """Test de gestión de configuración."""
    # Configurar desde diccionario
    config_dict = {
        "assistant_name": "DictConfig",
        "log_level": "ERROR",
        "processing_timeout": 60
    }
    
    config = Config(**config_dict)
    
    assert config.assistant_name == "DictConfig"
    assert config.log_level == "ERROR"
    assert config.processing_timeout == 60


# Test de logging
def test_logging_configuration():
    """Test de configuración de logging."""
    import logging
    
    # Verificar que el logger se crea correctamente
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"


# Parametrización de tests
@pytest.mark.parametrize("message_content,expected_sentiment", [
    ("I love this product", "positive"),
    ("This is terrible", "negative"),
    ("It's okay", "neutral")
])
def test_sentiment_analysis(message_content, expected_sentiment):
    """Test parametrizado de análisis de sentimiento."""
    # Simular función de análisis de sentimiento
    def analyze_sentiment(content: str) -> str:
        if "love" in content.lower():
            return "positive"
        elif "terrible" in content.lower():
            return "negative"
        else:
            return "neutral"
    
    sentiment = analyze_sentiment(message_content)
    assert sentiment == expected_sentiment


# Tests de integración
async def test_full_workflow(test_assistant):
    """Test de flujo completo del asistente."""
    workflow_messages = [
        "Initial message",
        "Follow-up message",
        "Final message"
    ]
    
    responses = []
    
    for content in workflow_messages:
        message = UserMessage(content=content)
        response = await test_assistant.process_input(message)
        responses.append(response)
    
    # Verificar el flujo completo
    assert len(responses) == 3
    assert all(isinstance(r, AssistantResponse) for r in responses)
    assert all("Test response for:" in r.content for r in responses)
    
    # Verificar que los mensajes fueron procesados en orden
    processed_contents = [msg.content for msg in test_assistant.processed_messages]
    assert processed_contents == workflow_messages


# Para ejecutar estos tests manualmente
def run_example_tests():
    """Ejecuta los tests de ejemplo."""
    print("=== Ejecutando Tests de Componentes ===\n")
    
    # Test 1: Inicialización
    print("1. Test de inicialización:")
    config = Config(assistant_name="TestAssistant", log_level="DEBUG")
    assistant = TestAssistant(config)
    print("   ✓ Asistente inicializado correctamente")
    assistant.cleanup()
    print()
    
    # Test 2: Validación de mensajes
    print("2. Test de validación de mensajes:")
    try:
        valid_message = UserMessage(content="Valid message")
        validate_message(valid_message)
        print("   ✓ Mensaje válido pasado la validación")
    except:
        print("   ✗ Error en validación de mensaje válido")
    
    try:
        invalid_message = UserMessage(content="")
        validate_message(invalid_message)
        print("   ✗ Mensaje inválido no rechazado")
    except ValueError:
        print("   ✓ Mensaje inválido correctamente rechazado")
    print()
    
    # Test 3: Procesamiento asíncrono
    print("3. Test de procesamiento asíncrono:")
    
    async def test_async_processing():
        config = Config(assistant_name="AsyncTest")
        assistant = TestAssistant(config)
        assistant.configure(config)
        
        message = UserMessage(content="Async test message")
        response = await assistant.process_input(message)
        
        assert isinstance(response, AssistantResponse)
        assert "Test response for:" in response.content
        
        assistant.cleanup()
        return True
    
    try:
        success = asyncio.run(test_async_processing())
        print("   ✓ Procesamiento asíncrono exitoso" if success else "   ✗ Error en procesamiento asíncrono")
    except Exception as e:
        print(f"   ✗ Error en procesamiento asíncrono: {e}")
    print()
    
    # Test 4: Configuración
    print("4. Test de configuración:")
    try:
        config_dict = {"assistant_name": "ConfigTest", "log_level": "INFO"}
        config = Config(**config_dict)
        assert config.assistant_name == "ConfigTest"
        assert config.log_level == "INFO"
        print("   ✓ Configuración desde diccionario exitosa")
    except Exception as e:
        print(f"   ✗ Error en configuración: {e}")
    print()
    
    print("Todos los tests de ejemplo completados.")


if __name__ == "__main__":
    run_example_tests()