# API de Utilidades

Esta documentación describe las utilidades y herramientas auxiliares del framework Asistente Osvaldo.

## LoggerFactory

### get_logger
```python
def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger configurado específico para un componente."""
```

## Fonética de Módulos

### Validation Module
```python
from assistant.interfaces.validation import (
    validate_message,
    validate_response,
    serialize_message,
    serialize_response,
    deserialize_message,
    deserialize_response
)
```

### Message Serialization
```python
def serialize_message(message: Message) -> Dict[str, Any]:
    """
    Serializa un mensaje a diccionario con formato estándar.
    
    Args:
        message: Objeto Message a serializar
        
    Returns:
        Dict[str, Any]: Representación en diccionario del mensaje
    """
```

**Ejemplo:**
```python
from assistant.interfaces.validation import serialize_message

message = UserMessage(content="Hola mundo", user_id="user_123")
serialized = serialize_message(message)

# Resultado:
# {
#     "content": "Hola mundo",
#     "message_type": "user",
#     "user_id": "user_123",
#     "timestamp": 1678901234.567
# }
```

### Deserialization
```python
def deserialize_message(data: Dict[str, Any]) -> Message:
    """
    Deserializa un diccionario al objeto de mensaje apropiado.
    
    Args:
        data: Diccionario con datos del mensaje
        
    Returns:
        Message: Objeto Message deserializado
        
    Raises:
        ValueError: Si los datos son inválidos o incompletos
    """
```

**Ejemplo:**
```python
from assistant.interfaces.validation import deserialize_message

data = {
    "content": "Hola mundo",
    "message_type": "user",
    "user_id": "user_123"
}

message = deserialize_message(data)
# Returns: UserMessage instance
```

## Config Utilities

### Config Validation
```python
from assistant.core.config_validator import (
    validate_config,
    get_validation_errors,
    validate_required_fields
)

def validate_required_fields(
    config: Config, 
    required_fields: List[str]
) -> bool:
    """
    Valida que los campos requeridos estén presentes y sean válidos.
    
    Args:
        config: Configuración a validar
        required_fields: Lista de nombres de campos requeridos
        
    Returns:
        bool: True si todos los campos requeridos son válidos
    """
```

### Environment-specific Configuration
```python
from assistant.core.environment_config import (
    get_config_for_environment,
    create_config_from_environment
)

def get_config_for_environment(
    environment: str,
    config_path: Optional[str] = None
) -> Config:
    """
    Obtiene configuración específica para un entorno.
    
    Args:
        environment: Nombre del entorno (development, staging, production)
        config_path: Ruta al archivo de configuración (opcional)
        
    Returns:
        Config: Configuración para el entorno especificado
    """
```

## Time and Performance Utilities

### Performance Timer
```python
import time
from typing import Optional

def timed_operation(func):
    """Decorador para medir tiempo de ejecución de funciones."""
    
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(
                f"Operation {func.__name__} completed",
                extra={
                    "operation": func.__name__,
                    "execution_time_ms": execution_time * 1000,
                    "success": True
                }
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Operation {func.__name__} failed",
                extra={
                    "operation": func.__name__,
                    "execution_time_ms": execution_time * 1000,
                    "success": False,
                    "error": str(e)
                }
            )
            raise
    
    return wrapper
```

**Uso:**
```python
@timed_operation
def process_large_dataset(dataset):
    # Procesamiento intensivo
    return processed_data
```

## Text Processing Utilities

### Text Helpers
```python
from assistant.utils.text import (
    normalize_text,
    extract_keywords,
    calculate_similarity,
    truncate_text
)

def normalize_text(text: str) -> str:
    """
    Normaliza texto eliminando caracteres especiales y normalizando espacios.
    
    Args:
        text: Texto a normalizar
        
    Returns:
        str: Texto normalizado
    """
```

### Token Counting
```python
def estimate_token_count(text: str) -> int:
    """
    Estima la cantidad de tokens que ocupará un texto.
    Aproximación 1 token ≈ 4 caracteres para inglés.
    
    Args:
        text: Texto a evaluar
        
    Returns:
        int: Estimación de token count
    """
```

## JSON Utilities

### Safe JSON Serialization
```python
import json
from typing import Any
from datetime import datetime

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder que maneja tipos especiales."""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, 'model_dump'):  # Pydantic models
            return obj.model_dump()
        if hasattr(obj, '__dict__'):  # Dataclasses y objetos
            return obj.__dict__
        return super().default(obj)

def safe_json_serialize(data: Any) -> str:
    """
    Serializa objeto a JSON de forma segura manejando tipos especiales.
    
    Args:
        data: Objeto a serializar
        
    Returns:
        str: JSON string
    """
    return json.dumps(data, cls=JSONEncoder, ensure_ascii=False)
```

### JSON Deserialization con Validación
```python
def safe_json_deserialize(json_str: str, expected_type: Optional[type] = None):
    """
    Deserializa JSON con validación opcional de tipo.
    
    Args:
        json_str: JSON string a deserializar
        expected_type: Tipo esperado para validación
        
    Returns:
        Objeto deserializado
    """
    try:
        data = json.loads(json_str)
        
        if expected_type and not isinstance(data, expected_type):
            raise ValueError(f"Expected {expected_type}, got {type(data)}")
            
        return data
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
```

## Retry Utilities

### Exponential Backoff Retry
```python
import time
import random
from typing import Callable, Any, Optional

class RetryConfig:
    """Configuración para política de retry."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    exceptions: tuple = (Exception,)
):
    """
    Decorador para retry con exponential backoff.
    
    Args:
        config: Configuración de retry
        exceptions: Tipos de excepción que activan retry
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            retry_config = config or RetryConfig()
            last_exception = None
            
            for attempt in range(retry_config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == retry_config.max_attempts - 1:
                        # Último intento, re-lanzar excepción
                        raise e
                    
                    # Calcular delay
                    delay = min(
                        retry_config.base_delay * 
                        (retry_config.backoff_factor ** attempt),
                        retry_config.max_delay
                    )
                    
                    # Agregar jitter si está habilitado
                    if retry_config.jitter:
                        delay *= (1 + random.random() * 0.1)
                    
                    time.sleep(delay)
                    continue
            
            # Nunca se debería llegar aquí
            raise last_exception
        
        return wrapper
    return decorator
```

**Ejemplo de uso:**
```python
from assistant.utils.retry import retry_with_backoff, RetryConfig

@retry_with_backoff(
    config=RetryConfig(
        max_attempts=5,
        base_delay=2.0,
        backoff_factor=2.0
    ),
    exceptions=(ConnectionError, TimeoutError)
)
def call_api_with_retry():
    # Llamada a API que puede fallar
    response = requests.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()
```

## Cache Utilities

### Memory Cache with Expiration
```python
from typing import Any, Optional, Callable
import time
from functools import wraps

class SimpleCache:
    """Cache simple en memoria con expiración."""
    
    def __init__(self, default_ttl: float = 3600):
        self.cache = {}
        self.default_ttl = default_ttl
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        expire_time = time.time() + (ttl or self.default_ttl)
        self.cache[key] = {
            "value": value,
            "expire_at": expire_time
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        entry = self.cache.get(key)
        if not entry or time.time() > entry["expire_at"]:
            # Expirado o no existe
            self.cache.pop(key, None)
            return default
        
        return entry["value"]
    
    def clear(self) -> None:
        self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """Limpia entradas expiradas y retorna cuántas eliminó."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time > entry["expire_at"]
        ]
        
        for key in expired_keys:
            self.cache.pop(key, None)
        
        return len(expired_keys)

# Implementación como decorador
cache = SimpleCache()

def memoize_with_cache(ttl: Optional[float] = None):
    """
    Decorador para memoizar funciones con cache y expiración.
    
    Args:
        ttl: Time to live en segundos para cache
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Crear clave única basada en argumentos
            cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Intentar obtener del cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator
```

**Ejemplo de uso:**
```python
from assistant.utils.cache import memoize_with_cache

@memoize_with_cache(ttl=10)  # Cache por 10 segundos
def expensive_computation(x: int, y: int) -> int:
    print(f"Computando {x} * {y}")  # Solo se verá la primera vez
    return x * y

# Primera llamada - ejecuta la función
result1 = expensive_computation(5, 3)  # Imprime "Computando 5 * 3"

# Segunda llamada - usa cache
result2 = expensive_computation(5, 3)  # No imprime nada
```

## Security Utilities

### Secure String Handling
```python
import hashlib
import hmac
import secrets
from typing import Optional

class SecurityUtils:
    """Utilidades para operaciones de seguridad básicas."""
    
    @staticmethod
    def hash_string(data: str, salt: Optional[str] = None) -> str:
        """
        Hashea un string usando SHA-256 con salt opcional.
        
        Args:
            data: String a hashear
            salt: Salt opcional (se genera si no se proporciona)
            
        Returns:
            str: Hash resultante
        """
        if not salt:
            salt = secrets.token_hex(16)
        
        hash_obj = hashlib.sha256(f"{salt}{data}".encode())
        return f"{salt}${hash_obj.hexdigest()}"
    
    @staticmethod
    def verify_hash(data: str, expected_hash: str) -> bool:
        """
        Verifica que un string coincida con un hash.
        
        Args:
            data: String original
            expected_hash: Hash con formato "salt$hash"
            
        Returns:
            bool: True si la verificación es exitosa
        """
        try:
            salt, hash_value = expected_hash.split('$', 1)
            computed_hash = SecurityUtils.hash_string(data, salt).split('$', 1)[1]
            return hmac.compare_digest(computed_hash, hash_value)
        except (ValueError, IndexError):
            return False
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Genera un token seguro criptográficamente.
        
        Args:
            length: Longitud del token en bytes
            
        Returns:
            str: Token seguro en formato hexadecimal
        """
        return secrets.token_hex(length)
```

**Ejemplo de uso:**
```python
from assistant.utils.security import SecurityUtils

# Hashear contraseña
password_hash = SecurityUtils.hash_string("mi_secreta")

# Verificar contraseña
is_valid = SecurityUtils.verify_hash("mi_secreta", password_hash)

# Generar token seguro para sesiones
session_token = SecurityUtils.generate_secure_token(16)
```