# API de Logging

Esta documentación describe el sistema de logging estructurado del framework Asistente Osvaldo.

## Sistema de Logging Centralizado

### get_logger

```python
def get_logger(name: str) -> logging.Logger
```
Obtiene un logger configurado específico para un componente.

**Parámetros:**
- `name`: Nombre del logger/componente

**Retorna:**
- `logging.Logger`: Logger configurado con handlers apropiados

**Ejemplo:**
```python
from assistant.utils import get_logger

# Obtener logger para un componente específico
logger = get_logger("assistant_core")
logger.info("Sistema inicializado", extra={"component": "core"})

# Logger para manejo de usuarios
user_logger = get_logger("user_management")
user_logger.info("Usuario creado", extra={"user_id": "user_123"})
```

### setup_logging

```python
def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    handlers: Optional[Dict[str, Dict[str, Any]]] = None
) -> None
```
Configura el sistema global de logging.

**Parámetros:**
- `level`: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `format_string`: Formato personalizado para los logs
- `handlers`: Diccionario de configuración de handlers

**Ejemplo:**
```python
from assistant.utils import setup_logging

# Configuración básica
setup_logging(level="INFO")

# Configuración personalizada
setup_logging(
    level="DEBUG",
    format_string="%(asctime)s [%(levelname)s] %(name)s: %(message)s | %(extra_fields)s",
    handlers={
        "console": {"level": "INFO"},
        "file": {
            "filename": "assistant.log",
            "level": "DEBUG",
            "max_bytes": 10485760,  # 10MB
            "backup_count": 5
        },
        "error_file": {
            "filename": "errors.log",
            "level": "ERROR"
        }
    }
)
```

## Logging Estructurado

### StructuredLogger

```python
class StructuredLogger:
    """Logger para generar logs en formato JSON estructurado."""
    
    def __init__(self, name: str, file_path: Optional[str] = None):
    def log(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None):
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
```

**Ejemplo:**
```python
from assistant.utils.structured_logging import StructuredLogger

# Crear logger estructurado
structured_logger = StructuredLogger("activity_tracker", "activity.json")

# Log estructurado con contexto
structured_logger.log(
    level="INFO",
    message="Procesamiento de solicitud completado",
    extra={
        "timestamp": time.time(),
        "user_id": "user_123",
        "request_id": "req_456",
        "processing_time_ms": 250,
        "success": True,
        "endpoint": "/api/chat",
        "model_used": "gpt-3.5-turbo"
    }
)

# Salida JSON:
# {"timestamp": 1678901234.567, "level": "INFO", "message": "Procesamiento de solicitud completado", 
#  "user_id": "user_123", "request_id": "req_456", "processing_time_ms": 250, "success": true, 
#  "endpoint": "/api/chat", "model_used": "gpt-3.5-turbo", "logger_name": "activity_tracker"}
```

## Logging de Performance

### PerformanceLogger

```python
class PerformanceLogger:
    """Logger especializado para métricas de rendimiento."""
    
    def __init__(self, name: str = "performance"):
    def log_operation(self, operation_name: str, duration_ms: float, **kwargs):
    def log_request(self, endpoint: str, response_time_ms: float, status_code: int, **kwargs):
```

**Ejemplo:**
```python
from assistant.utils.performance_logger import PerformanceLogger, performance_logger

# Obtener logger para un componente específico
perf_logger = PerformanceLogger("db_operations")

# Medir operaciones
perf_logger.log_operation(
    operation_name="database_query",
    duration_ms=125,
    query_type="SELECT",
    table="users",
    rows_returned=50
)

# Usar el decorador de rendimiento
perf_logger = performance_logger("assistant_processing")
perf_logger.log_operation(
    operation_name="text_generation",
    duration_ms=1500,
    model="gpt-4",
    input_tokens=200,
    output_tokens=150,
    temperature=0.7
)
```

### performance_logger (Función de conveniencia)

```python
def performance_logger(component_name: str) -> PerformanceLogger
```
Función de conveniencia para obtener un PerformanceLogger.

## Manejo de Excepciones y Errores

### ExceptionLogger

```python
class ExceptionLogger:
    """Logger especializado para registrar excepciones con contexto completo."""
    
    def __init__(self, name: str = "exceptions"):
    def log_exception(self, exception: Exception, context: Optional[Dict[str, Any]] = None):
    def log_with_traceback(self, message: str, level: str = "ERROR"):
```

**Ejemplo:**
```python
from assistant.utils.exception_logger import ExceptionLogger

exception_logger = ExceptionLogger("assistant_exceptions")

try:
    # Código que puede fallar
    result = risky_operation()
except Exception as e:
    # Log automático con contexto
    exception_logger.log_exception(
        exception=e,
        context={
            "user_id": "user_123",
            "operation": "process_message",
            "input_data": {"message": "Hola mundo"},
            "config": {"model": "gpt-3.5-turbo"}
        }
    )
```

## Logs con Contexto Enriquecido

### Context-aware Logging

```python
from assistant.utils import get_logger

logger = get_logger("assistant_api")

# Log con contexto estructurado
def process_user_message(user_id: str, message: str):
    logger.info(
        "Iniciando procesamiento de mensaje",
        extra={
            "user_id": user_id,
            "message_length": len(message),
            "has_attachments": False,
            "processing_stage": "start"
        }
    )
    
    try:
        # Simular procesamiento
        response = generate_response(message)
        
        logger.info(
            "Procesamiento completado exitosamente",
            extra={
                "user_id": user_id,
                "response_length": len(response),
                "processing_stage": "completed",
                "success": True
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "Error en procesamiento de mensaje",
            exc_info=True,  # Incluir stack trace
            extra={
                "user_id": user_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "processing_stage": "error",
                "success": False
            }
        )
        raise
```

## Handlers de Logging Especializados

### JSON File Handler

```python
from assistant.utils.logging import create_json_handler

# Crear handler que escribe logs en JSON
json_handler = create_json_handler(
    filename="activity.json",
    level="INFO"
)

# Agregar al logger
logger = get_logger("api")
logger.addHandler(json_handler)
```

### Rotating File Handler con Compresión

```python
from assistant.utils.logging import create_rotating_handler

# Handler con rotación automática y compresión
rotating_handler = create_rotating_handler(
    filename="app.log",
    max_bytes=50*1024*1024,  # 50MB
    backup_count=5,          # 5 archivos de backup
    compress=True            # Comprimir backups
)
```

### Slack/Team Notifications Handler

```python
from assistant.utils.logging import create_notification_handler

# Handler que envía errores críticos a Slack
slack_handler = create_notification_handler(
    webhook_url="https://hooks.slack.com/services/...",
    level="CRITICAL",
    channel="#alerts",
    username="Osvaldo Assistant"
)
```

## Métricas y Monitoreo

### Log Metrics Formatter

```python
from assistant.utils.logging import MetricsLogger

metrics_logger = MetricsLogger("assistant_metrics")

# Registrar métricas personalizadas
metrics_logger.log_metric(
    metric_name="daily_requests",
    value=1250,
    unit="count",
    dimensions={"region": "us-east-1", "model": "gpt-4"}
)

metrics_logger.log_metric(
    metric_name="response_time_p95",
    value=1500,
    unit="milliseconds"
)
```

### Health Check Logging

```python
def log_system_health():
    """Genera un resumen de salud del sistema."""
    
    import psutil
    import time
    
    logger = get_logger("health_check")
    
    logger.info(
        "Estado de salud del sistema",
        extra={
            "timestamp": time.time(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "active_sessions": get_active_session_count(),
            "pending_requests": get_pending_request_count(),
            "error_rate_24h": get_error_rate_24h()
        }
    )

# Programar logs de salud cada 5 minutos
import asyncio

async def health_check_loop():
    while True:
        log_system_health()
        await asyncio.sleep(300)  # 5 minutos
```

## Recomendaciones de Logging

### Estructura de Campos

El framework recomienda usar estos campos estándar:

```python
# Campos temporales
{
    "timestamp": 1678901234.567,      # Timestamp Unix
    "datetime": "2023-03-15T14:30:34.567Z"  # ISO 8601
}

# Campos de usuario/sesión
{
    "user_id": "user_123",            # ID único del usuario
    "session_id": "sess_456",         # ID de la sesión
    "request_id": "req_789"            # ID único de la solicitud
}

# Campos de operación
{
    "operation": "text_generation",    # Nombre de la operación
    "component": "assistant_core",     # Componente responsable
    "processing_stage": "queue"        # Etapa del procesamiento
}

# Campos de rendimiento
{
    "duration_ms": 1250,              # Duración en milisegundos
    "timing_breakdown": {              # Desglose de tiempos
        "validation": 50,
        "processing": 1150,
        "response": 50
    }
}

# Campos de resultado
{
    "success": True,                   # Indicador de éxito
    "error_code": None,                # Código de error si aplica
    "response_size": 1024             # Tamaño de la respuesta en bytes
}
```

### Niveles de Logging Apropiados

```python
logger.debug("Detalle interno", extra={"internal_state": {...}})

logger.info("Eventos normales", extra={"user_action": "button_click"})

logger.warning("Problemas no críticos", extra={"degraded_functionality": "cache_misses_high"})

logger.error("Errores manejables", extra={"recovered": True, "retry_count": 3})

logger.critical("Errores críticos", extra={"service_unavailable": True, "impact": "all_users"})
```