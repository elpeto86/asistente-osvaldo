# API del Asistente - BaseAssistant

Esta documentación describe la API principal para crear y gestionar asistentes de IA.

## Clase BaseAssistant

`BaseAssistant` es una clase abstracta que define la interfaz común para todas las implementaciones de asistentes.

### Constructor

```python
BaseAssistant(config: Optional[Config] = None, **kwargs)
```

**Parámetros:**
- `config` (opcional): Instancia de `Config`. Si no se proporciona, se genera automáticamente.
- `**kwargs`: Opciones de configuración adicionales.

**Ejemplo:**
```python
# Con configuración explícita
config = Config(name="MiAsistente", log_level="INFO")
assistant = MiAsistente(config)

# Sin configuración (generada automáticamente)
assistant = MiAsistente(log_level="DEBUG")
```

### Propiedades

#### name
```python
@property
def name(self) -> str
```
Obtiene el nombre del asistente desde la configuración.

#### status
```python
@property
def status(self) -> str
```
Obtiene el estado actual del asistente. Posibles valores:
- `INITIALIZING`: Inicializando
- `READY`: Listo para procesar
- `PROCESSING`: Procesando solicitud
- `ERROR`: Estado de error
- `PAUSED`: Pausado
- `SHUTTING_DOWN`: Apagándose

#### metrics
```python
@property
def metrics(self) -> AssistantMetrics
```
Obtiene las métricas de rendimiento del asistente.

#### context
```python
@property
def context(self) -> Dict[str, Any]
```
Obtiene los datos de contexto del asistente (copia para seguridad).

### Métodos Abstractos

#### process_input
```python
@abstractmethod
def process_input(
    self, 
    message: Union[Message, str, dict], 
    **kwargs
) -> AssistantResponse
```
Procesa la entrada del usuario y genera una respuesta.

**Parámetros:**
- `message`: Mensaje del usuario (objeto Message, string o diccionario)
- `**kwargs`: Opciones adicionales de procesamiento

**Retorna:**
- `AssistantResponse`: Respuesta del asistente

**Ejemplo:**
```python
def process_input(self, message, **kwargs):
    content = message.content if hasattr(message, 'content') else str(message)
    response_content = f"Procesado: {content}"
    return AssistantResponse(
        content=response_content,
        confidence=0.9
    )
```

#### configure
```python
@abstractmethod
def configure(self) -> None
```
Configura el asistente con ajustes y recursos. Se llama durante la inicialización.

#### cleanup
```python
@abstractmethod
def cleanup(self) -> None
```
Limpia recursos y cierra el asistente. Se llama durante el apagado.

### Métodos Concretos

#### process_input_async
```python
def process_input_async(
    self, 
    message: Union[Message, str, dict], 
    **kwargs
) -> Future[AssistantResponse]
```
Wrapper asíncrono para `process_input`.

#### Gestión de Contexto
```python
def set_context_value(self, key: str, value: Any) -> None
def get_context_value(self, key: str, default: Any = None) -> Any
def clear_context(self) -> None
```

**Ejemplo:**
```python
# Guardar un valor en el contexto
assistant.set_context_value("user_preference", "dark_mode")

# Obtener un valor del contexto
theme = assistant.get_context_value("user_preference", "light_mode")

# Limpiar todo el contexto
assistant.clear_context()
```

#### Gestión de Eventos
```python
def add_event_handler(self, event: str, handler: callable) -> None
def remove_event_handler(self, event: str, handler: callable) -> bool
```

**Eventos disponibles:**
- `initialized`: El asistente se ha inicializado
- `status_changed`: El estado del asistente ha cambiado
- `context_cleared`: El contexto ha sido limpiado
- `metrics_reset`: Las métricas han sido reiniciadas
- `error`: Ocurrió un error

**Ejemplo:**
```python
# Agregar manejador de eventos
def on_status_change(event: str, data: dict):
    print(f"Estado cambió a: {data['new_status']}")

assistant.add_event_handler("status_changed", on_status_change)

# Remover manejador
assistant.remove_event_handler("status_changed", on_status_change)
```

#### Gestión de Estado y Métricas
```python
def update_status(self, status: str) -> None
def reset_metrics(self) -> None
def get_health_status(self) -> Dict[str, Any]
```

**Ejemplo:**
```python
# Actualizar estado manualmente
assistant.update_status(AssistantStatus.PROCESSING)

# Reiniciar métricas
assistant.reset_metrics()

# Obtener estado de salud
health = assistant.get_health_status()
print(f"Tasa de éxito: {health['success_rate']}%")
```

### Clases Auxiliares

#### AssistantStatus
```python
class AssistantStatus:
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    PAUSED = "paused"
    SHUTTING_DOWN = "shutting_down"
```

#### AssistantMetrics
```python
@dataclass
class AssistantMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    uptime_seconds: float = 0.0
    last_request_time: Optional[float] = None
    
    @property
    def success_rate(self) -> float
    
    def increment_success(self, response_time_ms: float) -> None
    def increment_failure(self) -> None
    def update_uptime(self, start_time: float) -> None
```

#### Excepciones
```python
class AssistantError(Exception):
    """Excepción base para errores del asistente."""

class ConfigurationError(AssistantError):
    """Error cuando la configuración es inválida."""

class ProcessingError(AssistantError):
    """Error cuando el procesamiento de entrada falla."""

class ResourceError(AssistantError):
    """Error cuando los recursos requeridos no están disponibles."""
```

### Ejemplo Completo de Implementación

```python
from assistant import BaseAssistant, UserMessage, AssistantMessage, Config
from assistant.core.assistant import AssistantStatus, AssistantMetrics

class MiAsistente(BaseAssistant):
    def __init__(self, config=None, **kwargs):
        super().__init__(config, **kwargs)
        
        # Agregar manejadores de eventos
        self.add_event_handler("initialized", self._on_initialized)
        self.add_event_handler("status_changed", self._on_status_change)
    
    def process_input(self, message, **kwargs):
        # Actualizar estado
        self.update_status(AssistantStatus.PROCESSING)
        
        try:
            # Procesar el mensaje
            content = str(message)
            
            # Simular procesamiento
            response_content = f"Respuesta para: {content}"
            
            # Actualizar métricas
            response_time = 100  # ms
            self.metrics.increment_success(response_time)
            
            # Crear respuesta
            response = AssistantResponse(
                content=response_content,
                confidence=0.9
            )
            
            # Restaurar estado
            self.update_status(AssistantStatus.READY)
            
            return response
            
        except Exception as e:
            # Registrar fallo
            self.metrics.increment_failure()
            self.update_status(AssistantStatus.ERROR)
            
            # Re-lanzar excepción
            raise ProcessingError(f"Error procesando mensaje: {str(e)}")
    
    def configure(self):
        # Configurar recursos iniciales
        self.set_context_value("initialized_at", time.time())
        
    def cleanup(self):
        # Limpiar recursos
        self.clear_context()
        self.update_status(AssistantStatus.SHUTTING_DOWN)
    
    def _on_initialized(self, event: str, data: dict):
        print(f"✓ Asistente {data['assistant']} inicializado")
    
    def _on_status_change(self, event: str, data: dict):
        print(f"Estado: {data['old_status']} → {data['new_status']}")

# Uso con context manager
with MiAsistente(name="Ejemplo") as assistant:
    # La configuración y limpieza se manejan automáticamente
    pass
```

### Compatibilidad con Context Manager

La clase `BaseAssistant` implementa el protocolo de context manager:

```python
# Uso con bloque with (se limpia automáticamente)
with MiAsistente() as assistant:
    response = assistant.process_input("Hola mundo")
    # cleanup() se llama automáticamente al salir del bloque

# Uso manual (debe llamar cleanup() explícitamente)
assistant = MiAsistente()
try:
    response = assistant.process_input("Hola mundo")
finally:
    assistant.cleanup()
```