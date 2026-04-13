"""
Logging Personalizado con el Asistente Osvaldo

Este ejemplo muestra cómo utilizar el sistema de logging estructurado
del framework con diferentes configuraciones y manejadores.
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Agregar el directorio src al path para importar el módulo
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from assistant import BaseAssistant, UserMessage, AssistantMessage, Config
from assistant.utils import get_logger, setup_logging, performance_logger
from assistant.utils.structured_logging import StructuredLogger


# Asistente con logging personalizado
class LoggingAssistant(BaseAssistant):
    """Asistente con diferentes tipos de logging configurados."""
    
    def __init__(self, config: Config):
        super().__init__(config)
        
        # Obtener diferentes tipos de loggers
        self.main_logger = get_logger("logging_assistant")
        self.performance_logger = get_logger("performance")
        self.security_logger = get_logger("security")
        
        # Logger estructurado para logs JSON
        self.structured_logger = StructuredLogger("activity_tracker")
        
        self.message_count = 0
    
    async def process_input(self, message: UserMessage) -> AssistantMessage:
        """Procesa mensajes con diferentes tipos de logging."""
        self.message_count += 1
        
        # Logging básico
        self.main_logger.info("Procesando mensaje de usuario", extra={
            "message_id": self.message_count,
            "content_length": len(message.content)
        })
        
        # Logging de rendimiento (medición de tiempo)
        start_time = time.time()
        
        # Simular procesamiento
        await asyncio.sleep(0.1)
        
        processing_time = time.time() - start_time
        
        # Registrar métricas de rendimiento
        self.performance_logger.info("Mensaje procesado", extra={
            "message_id": self.message_count,
            "processing_time_ms": processing_time * 1000,
            "throughput_msg_per_sec": 1 / processing_time
        })
        
        # Logging de seguridad (si hay contenido sensible)
        if "password" in message.content.lower() or "token" in message.content.lower():
            self.security_logger.warning("Contenido potencialmente sensible detectado", extra={
                "message_id": self.message_count,
                "content_preview": message.content[:50]
            })
        
        # Logging estructurado en JSON
        self.structured_logger.log(
            level="INFO",
            message="Actividad de procesamiento",
            extra={
                "activity_type": "message_processing",
                "message_id": self.message_count,
                "user_id": getattr(message, 'user_id', 'anonymous'),
                "processing_time_ms": processing_time * 1000,
                "content_length": len(message.content),
                "timestamp": time.time()
            }
        )
        
        # Logging de excepciones con contexto
        try:
            # Simular procesamiento que podría fallar
            if len(message.content) > 100:
                raise ValueError("Mensaje demasiado largo para procesamiento rápido")
            
            # Generar respuesta
            response_content = f"Mensaje #{self.message_count} procesado correctamente"
            
        except Exception as e:
            self.main_logger.error(
                "Error durante el procesamiento del mensaje",
                exc_info=True,
                extra={
                    "message_id": self.message_count,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            )
            
            response_content = f"Error procesando mensaje #{self.message_count}: {str(e)}"
        
        return AssistantMessage(
            content=response_content,
            confidence=0.95
        )
    
    def configure(self, config: Config) -> None:
        self.main_logger.info("Configurando LoggingAssistant")
    
    def cleanup(self) -> None:
        self.main_logger.info(f"Cleanup: Se procesaron {self.message_count} mensajes")


def demonstrate_basic_logging():
    """Demonstrates basic logging configuration."""
    print("1. Logging Básico:")
    
    # Configurar logging básico
    setup_logging(
        level="INFO",
        format_string="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger = get_logger("demo_basic")
    
    logger.debug("Este es un mensaje de debug")
    logger.info("Este es un mensaje de info")
    logger.warning("Este es un mensaje de advertencia")
    logger.error("Este es un mensaje de error")
    
    print("   ✓ Logs básicos generados en consola")
    print()


def demonstrate_file_logging():
    """Demonstrates logging to files."""
    print("2. Logging a Archivo:")
    
    # Configurar logging a archivo
    log_file = "assistant_activity.log"
    setup_logging(
        level="INFO",
        handlers={
            "file": {
                "filename": log_file,
                "level": "DEBUG",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    )
    
    logger = get_logger("demo_file")
    
    logger.info("Este mensaje se guardará en el archivo log")
    logger.debug("Este mensaje de debug también se guardará")
    
    # Verificar que el archivo se creó
    log_path = Path(log_file)
    if log_path.exists():
        print(f"   ✓ Logs guardados en: {log_file}")
        print(f"   Tamaño del archivo: {log_path.stat().st_size} bytes")
        log_path.unlink()  # Limpiar después de la demostración
    print()


def demonstrate_json_logging():
    """Demonstrates structured JSON logging."""
    print("3. Logging Estructurado (JSON):")
    
    log_file = "assistant_structured.log"
    structured_logger = StructuredLogger("demo_structured", file_path=log_file)
    
    # Log con contexto estructurado
    structured_logger.log(
        level="INFO",
        message="Usuario interactuó con el sistema",
        extra={
            "user_id": "user_123",
            "action": "message_sent",
            "timestamp": time.time(),
            "session_id": "sess_456"
        }
    )
    
    structured_logger.log(
        level="WARNING",
        message="Umbral de rendimiento excedido",
        extra={
            "metric": "response_time",
            "value": 2.5,
            "threshold": 1.0,
            "unit": "seconds"
        }
    )
    
    # Mostrar el contenido JSON generado
    if Path(log_file).exists():
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():  # Ignorar líneas vacías
                    try:
                        log_data = json.loads(line)
                        print(f"   JSON Log: {json.dumps(log_data, indent=2)}")
                    except json.JSONDecodeError:
                        pass
        
        Path(log_file).unlink()  # Limpiar
    print()


def demonstrate_performance_logging():
    """Demonstrates performance logging."""
    print("4. Logging de Rendimiento:")
    
    perf_logger = performance_logger("demo_performance")
    
    # Medir rendimiento de diferentes operaciones
    operations = [
        ("Procesamiento rápido", 0.05),
        ("Procesamiento normal", 0.2),
        ("Procesamiento lento", 0.5)
    ]
    
    for name, duration in operations:
        start_time = time.time()
        time.sleep(duration)  # Simular operación
        end_time = time.time()
        
        perf_logger.log_operation(
            operation_name=name,
            start_time=start_time,
            end_time=end_time,
            extra={"operation_type": "processing"}
        )
        
        print(f"   ✓ {name}: {(end_time - start_time) * 1000:.1f}ms")
    print()


async def demonstrate_exception_logging():
    """Demonstrates exception logging with context."""
    print("5. Logging de Excepciones:")
    
    logger = get_logger("demo_exceptions")
    
    # Simular diferentes tipos de excepciones
    exception_scenarios = [
        ("TimeoutError", lambda: asyncio.sleep(1000)),
        ("ValueError", lambda: int("no_numero")),
        ("KeyError", lambda: {"clave": "valor"}["no_existe"])
    ]
    
    for name, function in exception_scenarios:
        logger.info(f"Probando escenario: {name}")
        
        try:
            if name == "TimeoutError":
                await asyncio.wait_for(function(), timeout=0.1)  # Esperar mucho, timeout corto
            else:
                function()
        except Exception as e:
            logger.error(
                f"Excepción capturada: {name}",
                exc_info=True,
                extra={
                    "exception_type": type(e).__name__,
                    "scenario": name,
                    "recovery_possible": False
                }
            )
    
    print("   ✓ Excepciones registradas con stack trace completo")
    print()


async def main():
    """Función principal del ejemplo de logging."""
    print("=== Logging Personalizado con Asistente Osvaldo ===\n")
    
    # Demostrar diferentes tipos de logging
    demonstrate_basic_logging()
    demonstrate_file_logging()
    demonstrate_json_logging()
    demonstrate_performance_logging()
    await demonstrate_exception_logging()
    
    # Demostrar asistente con logging avanzado
    print("6. Asistente con Logging Integrado:")
    
    config = Config(
        assistant_name="LoggingDemo",
        log_level="INFO"
    )
    
    assistant = LoggingAssistant(config)
    assistant.configure(config)
    
    # Probar el asistente con diferentes tipos de mensajes
    messages = [
        "Mensaje normal para procesamiento",
        "Este mensaje contiene la palabra password, debe generar un log de seguridad",
        "Este es un mensaje extremadamente largo que debería causar un error de procesamiento para demostrar el logging de excepciones con contexto adicional"
    ]
    
    for message in messages:
        print(f"   Enviando: {message[:50]}{'...' if len(message) > 50 else ''}")
        user_message = UserMessage(content=message)
        response = await assistant.process_input(user_message)
        print(f"   Respuesta: {response.content[:50]}")
    
    assistant.cleanup()
    print()
    print("Demostración de logging completada.")


if __name__ == "__main__":
    asyncio.run(main())