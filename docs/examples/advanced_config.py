"""
Configuración Avanzada del Asistente Osvaldo

Este ejemplo muestra cómo utilizar las diferentes fuentes de configuración
del framework: variables de entorno, archivos .env y configuración YAML.
"""

import asyncio
import os
import sys
from pathlib import Path

# Agregar el directorio src al path para importar el módulo
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from assistant import BaseAssistant, UserMessage, AssistantMessage, Config
from assistant.core.config_loader import ConfigLoader
from assistant.core.environment_config import EnvironmentConfig
from assistant.utils import get_logger


# Asistente con configuración avanzada
class AdvancedAssistant(BaseAssistant):
    """Asistente con configuración avanzada y múltiples fuentes de datos."""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.logger = get_logger("advanced_assistant")
        
        # Acceder a diferentes partes de la configuración
        self.processing_timeout = getattr(config, 'processing_timeout', 30)
        self.max_response_length = getattr(config, 'max_response_length', 500)
        self.feature_flags = getattr(config, 'feature_flags', {})
    
    async def process_input(self, message: UserMessage) -> AssistantMessage:
        """Procesa mensajes con configuración avanzada."""
        self.logger.info(
            "Procesando con configuración avanzada",
            extra={
                "timeout": self.processing_timeout,
                "max_length": self.max_response_length,
                "features": self.feature_flags
            }
        )
        
        # Aplicar configuración específica si está habilitada
        if self.feature_flags.get('enable_capitalization', False):
            content = message.content.upper()
        else:
            content = message.content
        
        # Limitar longitud de respuesta si está configurado
        if len(content) > self.max_response_length:
            content = content[:self.max_response_length] + "..."
        
        return AssistantMessage(
            content=f"Respuesta configurada: {content}",
            confidence=0.9
        )
    
    def configure(self, config: Config) -> None:
        self.logger.info("Configurando AdvancedAssistant")
    
    def cleanup(self) -> None:
        self.logger.info("Limpiando recursos del AdvancedAssistant")


def demonstrate_env_config():
    """Demonstrates configuration from environment variables."""
    print("1. Configuración desde variables de entorno:")
    
    # Establecer variables de entorno para el ejemplo
    os.environ['ASSISTANT_NAME'] = 'EnvAssistant'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    os.environ['PROCESSING_TIMEOUT'] = '45'
    
    config = Config.from_environ()
    print(f"   Nombre del asistente: {config.assistant_name}")
    print(f"   Nivel de log: {config.log_level}")
    print()


def demonstrate_file_config():
    """Demonstrates configuration from .env file."""
    print("2. Configuración desde archivo .env:")
    
    # Crear un archivo .env de ejemplo
    env_content = """
ASSISTANT_NAME=FileAssistant
LOG_LEVEL=INFO
PROCESSING_TIMEOUT=60
MAX_RESPONSE_LENGTH=200
FEATURE_FLAGS={"enable_capitalization": true, "enable_logging": false}
"""
    
    env_file = Path(".env.example")
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    config = Config.from_env(str(env_file))
    print(f"   Nombre del asistente: {config.assistant_name}")
    print(f"   Timeout de procesamiento: {config.processing_timeout}")
    print(f"   Máxima longitud de respuesta: {config.max_response_length}")
    
    # Limpiar archivo de ejemplo
    env_file.unlink()
    print()


def demonstrate_yaml_config():
    """Demonstrates configuration from YAML file."""
    print("3. Configuración desde archivo YAML:")
    
    # Crear un archivo YAML de ejemplo
    yaml_content = """
assistant_name: YamlAssistant
log_level: WARNING
processing_timeout: 120
max_response_length: 1000
feature_flags:
  enable_capitalization: true
  enable_logging: true
  enable_metrics: false
additional_settings:
  theme: dark
  language: es
"""
    
    yaml_file = Path("config_example.yaml")
    with open(yaml_file, 'w') as f:
        f.write(yaml_content)
    
    config = Config.from_yaml(str(yaml_file))
    print(f"   Nombre del asistente: {config.assistant_name}")
    print(f"   Flags de características: {config.feature_flags}")
    
    # Limpiar archivo de ejemplo
    yaml_file.unlink()
    print()


def demonstrate_multi_source_config():
    """Demonstrates configuration from multiple sources with priority."""
    print("4. Configuración multi-fuente (con prioridad):")
    
    # Crear archivo .env
    env_content = """
ASSISTANT_NAME=EnvOverride
LOG_LEVEL=ERROR
"""
    
    env_file = Path(".env.priority")
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    # Configurar variables de ambiente (menor prioridad)
    os.environ['ASSISTANT_NAME'] = 'EnvLowPriority'
    os.environ['PROCESSING_TIMEOUT'] = '30'
    
    # Cargar configuración con diferentes prioridades
    config_loader = ConfigLoader()
    config = config_loader.load_config(
        env_file=str(env_file),
        env_prefix='ASSISTANT_',
        use_environ=True
    )
    
    print(f"   Nombre (de .env, override): {config.assistant_name}")
    print(f"   Nivel de log (de .env): {config.log_level}")
    print(f"   Timeout (de variables de entorno): {config.processing_timeout}")
    
    # Limpiar archivo de ejemplo
    env_file.unlink()
    print()


async def demonstrate_advanced_assistant():
    """Demonstrates the advanced assistant in action."""
    print("5. Asistente con configuración avanzada en acción:")
    
    # Configurar un asistente con opción de mayúsculas
    config = Config(
        assistant_name="AdvancedDemo",
        log_level="INFO",
        processing_timeout=45,
        max_response_length=300,
        feature_flags={
            "enable_capitalization": True,
            "enable_logging": True
        }
    )
    
    assistant = AdvancedAssistant(config)
    assistant.configure(config)
    
    # Probar el asistente
    messages = [
        "Este es un mensaje corto",
        "Este es un mensaje mucho más largo que será truncado por la configuración de longitud máxima de respuesta configurada en el sistema"
    ]
    
    for message in messages:
        user_message = UserMessage(content=message)
        response = await assistant.process_input(user_message)
        print(f"   Entrada: {message[:50]}{'...' if len(message) > 50 else ''}")
        print(f"   Salida: {response.content}")
    
    assistant.cleanup()
    print()


async def main():
    """Función principal del ejemplo de configuración avanzada."""
    print("=== Configuración Avanzada del Asistente Osvaldo ===\n")
    
    # Demostrar diferentes métodos de configuración
    demonstrate_env_config()
    demonstrate_file_config()
    demonstrate_yaml_config()
    demonstrate_multi_source_config()
    await demonstrate_advanced_assistant()
    
    print("Configuración avanzada completada.")


if __name__ == "__main__":
    asyncio.run(main())