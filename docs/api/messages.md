# API de Mensajes

Esta documentación describe el sistema de mensajería del framework Asistente Osvaldo, que define los tipos de mensajes y su validación.

## Clases de Mensajes

### Message (Clase Base)

```python
@dataclass
class Message(ABC):
    """Clase base abstracta para todos los tipos de mensajes."""

    @property
    @abstractmethod
    def content(self) -> str:
        """Contenido del mensaje."""

    @property
    @abstractmethod
    def message_type(self) -> str:
        """Tipo del mensaje."""

    def to_dict(self) -> Dict[str, Any]:
        """Convertir mensaje a diccionario."""

    def to_json(self) -> str:
        """Convertir mensaje a JSON string."""
```

### UserMessage

```python
@dataclass
class UserMessage(Message):
    """
    Mensaje enviado por un usuario al asistente.
    
    Args:
        content: Contenido del mensaje
        user_id: ID opcional del usuario
        timestamp: Marca de tiempo (automática si no se proporciona)
        metadata: Metadatos opcionales del mensaje
    """
```

**Constructor:**
```python
UserMessage(
    content: str,
    user_id: Optional[str] = None,
    timestamp: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
)
```

**Ejemplo:**
```python
# Mensaje simple
message = UserMessage(content="Hola, ¿cómo estás?")

# Con metadatos
message = UserMessage(
    content="Necesito ayuda con Python",
    user_id="user_123",
    metadata={
        "source": "web_interface",
        "language": "es",
        "priority": "medium"
    }
)
```

### AssistantMessage

```python
@dataclass
class AssistantMessage(Message):
    """
    Mensaje enviado por el asistente al usuario.
    
    Args:
        content: Contenido de la respuesta
        confidence: Nivel de confianza de la respuesta (0.0-1.0)
        timestamp: Marca de tiempo (automática si no se proporciona)
        processing_time_ms: Tiempo de procesamiento en milisegundos
        metadata: Metadatos opcionales del mensaje
    """
```

**Constructor:**
```python
AssistantMessage(
    content: str,
    confidence: float,
    timestamp: Optional[float] = None,
    processing_time_ms: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
)
```

**Ejemplo:**
```python
# Respuesta simple
response = AssistantMessage(
    content="Estoy bien, ¿en qué puedo ayudarte?",
    confidence=0.95
)

# Con información detallada
response = AssistantMessage(
    content="Para instalar Python, sigue estos pasos...",
    confidence=0.87,
    processing_time_ms=1250,
    metadata={
        "model": "gpt-3.5-turbo",
        "tokens_used": 156,
        "source": "knowledge_base"
    }
)
```

### SystemMessage

```python
@dataclass
class SystemMessage(Message):
    """
    Mensaje interno del sistema para instrucciones o control.
    
    Args:
        content: Contenido del mensaje de sistema
        severity: Nivel de severidad (INFO, WARNING, ERROR, CRITICAL)
        timestamp: Marca de tiempo (automática si no se proporciona)
        metadata: Metadatos opcionales del mensaje
    """
```

**Ejemplo:**
```python
# Mensaje de información
system_msg = SystemMessage(
    content="Asistente inicializado correctamente",
    severity="INFO"
)

# Mensaje de error
system_msg = SystemMessage(
    content="API key expirada, requiere renovación",
    severity="CRITICAL",
    metadata={"error_code": "AUTH_EXPIRED"}
)
```

## Clase AssistantResponse

```python
@dataclass
class AssistantResponse:
    """
    Respuesta estructurada del asistente con metadatos adicionales.
    
    Esta clase extiende básicamente AssistantMessage con validación adicional
    y soporte para diferentes tipos de contenido.
    """
```

**Constructor:**
```python
AssistantResponse(
    content: str,
    confidence: float,
    metadata: Optional[Dict[str, Any]] = None,
    response_type: str = "text",
    timestamp: Optional[float] = None,
    processing_time_ms: Optional[float] = None
)
```

**Ejemplo:**
```python
# Respuesta básica
response = AssistantResponse(
    content="Respuesta a tu consulta",
    confidence=0.92
)

# Respuesta con diferentes tipos de contenido
response = AssistantResponse(
    content="Datos procesados correctamente",
    confidence=0.98,
    response_type="status",
    metadata={
        "operation": "data_processing",
        "records_processed": 1500,
        "success_rate": 0.987
    }
)
```

## Métodos de Validación

### validate_message
```python
def validate_message(message: Message) -> bool
```
Valida que un mensaje cumpla con los requisitos de formato y datos.

**Valida:**
- Contenido no vacío
- Tiempo de procesamiento no negativo
- Confianza entre 0.0 y 1.0

**Ejemplo:**
```python
from assistant.interfaces.validation import validate_message

message = UserMessage(content="Hola")
is_valid = validate_message(message)
```

### validate_response
```python
def validate_response(response: AssistantResponse) -> bool
```
Valida que una respuesta cumpla con los requisitos mínimos.

### serialize_message
```python
def serialize_message(message: Message) -> Dict[str, Any]
```
Serializa un mensaje a un diccionario con formato estándar.

### deserialize_message
```python
def deserialize_message(data: Dict[str, Any]) -> Message
```
Deserializa un diccionario al objeto de mensaje apropiado.

**Ejemplo:**
```python
from assistant.interfaces.validation import serialize_message, deserialize_message

# Serializar a diccionario
message_dict = serialize_message(user_message)

# Deserializar de vuelta a objeto
restored_message = deserialize_message(message_dict)
```

## Conversión entre Tipos

\`\`\`python
# De UserMessage a AssistantMessage con conversión automática
def create_response_from_message(user_message: UserMessage, content: str) -> AssistantMessage:
    return AssistantMessage(
        content=content,
        confidence=0.9,
        processing_time_ms=None
    )

# Crear una respuesta JSON estructurada
def create_json_response(data: Dict[str, Any], confidence: float = 1.0) -> AssistantResponse:
    import json
    
    return AssistantResponse(
        content=json.dumps(data, indent=2),
        confidence=confidence,
        response_type="json",
        metadata={"content_type": "application/json"}
    )
\`\`\`

## Manejo de Errores de Validación

\`\`\`python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def safe_validate_message(message: Message) -> bool:
    """
    Validación segura con logging de errores.
    
    Returns:
        bool: True si es válido, False en caso contrario
    """
    try:
        return validate_message(message)
    except ValueError as e:
        logger.error(f"Error de validación en mensaje: {e}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado validando mensaje: {e}")
        return False

def safe_deserialize(data: Dict[str, Any]) -> Optional[Message]:
    """
    Deserialización segura con manejo de errores.
    
    Returns:
        Optional[Message]: Mensaje deserializado o None si falla
    """
    try:
        return deserialize_message(data)
    except Exception as e:
        logger.error(f"Error deserializando mensaje: {e}")
        return None
\`\`\`

## Patrones de Uso Avanzados

### Mensajes con Encadenamiento de Contexto

\`\`\`python
@dataclass
class ContextualMessage(Message):
    """Mensaje con información de contexto y encadenamiento."""
    previous_message_id: Optional[str] = None
    conversation_id: str
    session_context: Optional[Dict[str, Any]] = None
    
    @property
    def content(self) -> str:
        return self._content
    
    @content.setter
    def content(self, value: str):
        self._content = value
    
    @property
    def message_type(self) -> str:
        return "contextual"

# Uso en conversación
conversation_id = "conv_123"
context_msg = ContextualMessage(
    content="¿Puedes explicarme esto mejor?",
    conversation_id=conversation_id,
    previous_message_id="msg_456",
    session_context={"topic": "python_programming"}
)
\`\`\`

### Mensajes con Metadata Enriquecida

\`\`\`python
def create_annotated_response(
    content: str, 
    confidence: float,
    annotations: Dict[str, Any] = None
) -> AssistantResponse:
    """Crea una respuesta con anotaciones estructuradas."""
    
    return AssistantResponse(
        content=content,
        confidence=confidence,
        metadata={
            "annotations": annotations or {},
            "generated_at": time.time(),
            "schema_version": "1.0",
            "source_system": "osvaldo_assistant"
        }
    )

# Uso
response = create_annotated_response(
    content="Python es un lenguaje de programación interpretado...",
    confidence=0.95,
    annotations={
        "topics": ["programming", "python", "interpreted_languages"],
        "reading_level": "intermediate",
        "estimated_reading_time_minutes": 2,
        "related_concepts": ["scripting", "dynamic_typing", "garbage_collection"]
    }
)
\`\`\`

### Streaming de Mensajes (Progresivos)

\`\`\`python
from typing import AsyncGenerator

async def stream_response(
    partial_content: str,
    confidence_func: Callable[[float], float]
) -> AsyncGenerator[PartialMessage, None]:
    """Genera mensajes parciales para respuestas en streaming."""
    
    words = partial_content.split()
    accumulated_text = ""
    
    for i, word in enumerate(words):
        accumulated_text += word + " "
        confidence = confidence_func(i / len(words))
        
        yield AssistantMessage(
            content=accumulated_text.strip(),
            confidence=confidence,
            metadata={"is_partial": True, "progress": (i + 1) / len(words)}
        )

# Uso
partial_messages = []
async for partial_msg in stream_response(
    "Esta es una respuesta larga que se generará gradualmente",
    lambda progress: 0.5 + progress * 0.5  # Confianza de 0.5 a 1.0
):
    partial_messages.append(partial_msg)
\`\`\`

## Metadatos Estándar

El framework recomienda usar los siguientes metadatos estándar:

\`\`\`python
# Metadatos de usuario
{
    "user_id": "user_123",           # Identificador del usuario
    "session_id": "session_456",     # sesión actual
    "source": "web_chat",           # interfaz o canal
    "language": "es",               # idioma preferido
    "timezone": "America/Mexico_City"  # zona horaria
}

# Metadatos de procesamiento
{
    "model": "gpt-4",                # modelo de IA utilizado
    "tokens_used": 256,              # tokens consumidos
    "processing_time_ms": 1250,      # tiempo de procesamiento
    "cache_hit": false,              # si se usó caché
    "error_rate": 0.02              # tasa de error
}

# Metadatos de contenido
{
    "content_type": "text",          # tipo de contenido
    "format": "markdown",            # formato del texto
    "reading_level": "intermediate", # nivel de lectura
    "word_count": 150,              # número de palabras
    "has_sensitive_data": false     # si contiene datos sensibles
}
\`\`\`