"""
Ejemplo básico del Asistente Osvaldo

Este ejemplo muestra cómo configurar y utilizar un asistente básico
con funcionalidades fundamentales del framework.
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio src al path para importar el módulo
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from assistant import BaseAssistant, UserMessage, AssistantMessage, Config
from assistant.utils import get_logger


# Implementación básica de un asistente
class EchoAssistant(BaseAssistant):
    """Asistente simple que repite mensajes con una transformación básica."""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger = get_logger("echo_assistant")
    
    async def process_input(self, message: UserMessage) -> AssistantMessage:
        """
        Procesa un mensaje del usuario devolviendo un eco del contenido.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            AssistantMessage: Respuesta del asistente
        """
        self.logger.info("Procesando mensaje", extra={
            "message_length": len(message.content),
            "user_id": getattr(message, 'user_id', None)
        })
        
        # Transformación simple: convertir a mayúsculas y añadir prefijo
        processed_content = f"ECO: {message.content.upper()}"
        
        return AssistantMessage(
            content=processed_content,
            confidence=0.95
        )
    
    def configure(self, config: Config) -> None:
        """Configura el asistente con los parámetros proporcionados."""
        self.logger.info("Configurando EchoAssistant")
        # Aquí se podrían establecer configuraciones adicionales
    
    def cleanup(self) -> None:
        """Realiza la limpieza de recursos."""
        self.logger.info("Limpiando recursos del EchoAssistant")


async def main():
    """Función principal del ejemplo."""
    
    # Configuración básica
    config = Config(
        assistant_name="EcoAssistant",
        log_level="INFO"
    )
    
    # Crear instancia del asistente
    assistant = EchoAssistant(config)
    
    try:
        # Configurar el asistente
        assistant.configure(config)
        
        # Mensajes de ejemplo
        messages = [
            "Hola, ¿cómo estás?",
            "¿Qué es el framework Osvaldo?",
            "Muéstrame un ejemplo de uso"
        ]
        
        print("=== Asistente Osvaldo - Ejemplo Básico ===\n")
        
        # Procesar cada mensaje
        for i, msg_content in enumerate(messages, 1):
            print(f"Usuario {i}: {msg_content}")
            
            user_message = UserMessage(content=msg_content, user_id=f"user_{i}")
            response = await assistant.process_input(user_message)
            
            print(f"Asistente: {response.content}")
            print(f"Confianza: {response.confidence:.2f}")
            print("-" * 50)
    
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
    finally:
        # Asegurar limpieza de recursos
        assistant.cleanup()


if __name__ == "__main__":
    # Ejecutar el ejemplo
    asyncio.run(main())