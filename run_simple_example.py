"""
Ejemplo simple del Asistente Osvaldo ejecutable
"""

import asyncio
import sys
import time
from pathlib import Path

# Agregar el directorio src al path para importar el módulo
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Usar las clases directamente si el import falla
try:
    from assistant.core.assistant import BaseAssistant
    from assistant.core.config import Config
    from assistant.interfaces.responses import AssistantResponse
    from typing import Union
    
    # Definir clases básicas si no importan correctamente
    print("OK: Importando clases del framework")
    
except ImportError as e:
    print(f"Error de importación: {e}")
    print("Creando clases básicas para demostración...")
    
    from abc import ABC, abstractmethod
    from typing import Any, Dict, Optional, Union
    import time
    
    class Config:
        def __init__(self, **kwargs):
            self.assistant_name = kwargs.get("assistant_name", "Osvaldo")
            self.log_level = kwargs.get("log_level", "INFO")
    
    class AssistantResponse:
        def __init__(self, content: str, confidence: float = 1.0):
            self.content = content
            self.confidence = confidence
    
    class BaseAssistant(ABC):
        def __init__(self, config: Optional[Config] = None):
            self.config = config or Config()
            self.context = {}
        
        @abstractmethod
        def process_input(self, message: Union[str, 'UserMessage'], **kwargs) -> AssistantResponse:
            """Procesar entrada de usuario."""
            pass
        
        @abstractmethod
        def configure(self) -> None:
            """Configurar el asistente."""
            pass
        
        @abstractmethod
        def cleanup(self) -> None:
            """Limpiar recursos."""
            pass
        
        def set_context_value(self, key: str, value: Any) -> None:
            """Establecer valor en contexto."""
            self.context[key] = value
        
        def get_context_value(self, key: str, default: Any = None) -> Any:
            """Obtener valor del contexto."""
            return self.context.get(key, default)
        
        def clear_context(self) -> None:
            """Limpiar contexto."""
            self.context.clear()
    
    class UserMessage:
        def __init__(self, content: str, user_id: Optional[str] = None):
            self.content = content
            self.user_id = user_id


class EchoAssistant(BaseAssistant):
    """Asistente simple que repite mensajes."""
    
    def __init__(self, config: Config = None):
        super().__init__(config)
        self.name = self.config.assistant_name if self.config else "EchoAssistant"
        print(f"INICIALIZANDO asistente: {self.name}")
    
    def process_input(self, message: Union[str, "UserMessage"], **kwargs) -> AssistantResponse:
        """Procesar mensaje y generar respuesta."""
        # Obtener contenido del mensaje
        if isinstance(message, str):
            content = message
        else:
            content = message.content
        
        print(f"RECIBIDO: {content}")
        
        # Procesamiento simple
        processed_content = f"{self.name} responde: Recibí tu mensaje '{content}'"
        
        # Crear respuesta
        response = AssistantResponse(
            content=processed_content,
            confidence=0.95
        )
        
        print(f"ENVIANDO respuesta con confianza: {response.confidence}")
        return response
    
    def configure(self) -> None:
        """Configurar el asistente."""
        print("Configurando asistente...")
        self.set_context_value("configured", True)
        self.set_context_value("config_time", time.time())
    
    def cleanup(self) -> None:
        """Limpiar recursos."""
        print("🧹 Limpiando recursos...")
        self.clear_context()


async def main():
    """Función principal del ejemplo."""
    
    print("=" * 60)
    print("Asistente Osvaldo - Ejemplo Simple")
    print("=" * 60)
    
    # Configuración
    config = Config(
        assistant_name="MiAsistente",
        log_level="INFO"
    )
    
    # Crear asistente
    assistant = EchoAssistant(config)
    
    try:
        # Configurar
        print("\nConfigurando sistema...")
        assistant.configure()
        print("Sistema configurado\n")
        
        # Mensajes de ejemplo
        messages = [
            "Hola, ¿cómo estás?",
            "¿Qué puedes hacer?",
            "Muéstrame un ejemplo",
            "Gracias!"
        ]
        
        print("Iniciando conversación...\n")
        
        for i, msg_content in enumerate(messages, 1):
            print(f"--- Mensaje {i} ---")
            print(f"Usuario: {msg_content}")
            
            # Procesar mensaje
            response = assistant.process_input(msg_content)
            
            print(f"Asistente: {response.content}")
            print(f"Confianza: {response.confidence:.2f}")
            print()
        
        print("Demostración completada!")
        
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\nFinalizando...")
        assistant.cleanup()
        print("Listo!")


if __name__ == "__main__":
    # Ejecutar ejemplo
    asyncio.run(main())