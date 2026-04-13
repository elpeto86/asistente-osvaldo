# API de Configuración

Esta documentación describe el sistema de gestión de configuración del framework Asistente Osvaldo.

## Clase Config

`Config` es una clase Pydantic que proporciona gestión centralizada de configuración con validación de tipos y soporte para múltiples orígenes de datos.

### Constructor

```python
class Config(BaseModel):
    pass
```

La clase `Config` define todos los campos de configuración con validación automática de tipos.

### Campos Principales

#### Información del Asistente
```python
name: str = "Osvaldo"
description: Optional[str] = None
version: str = "1.0.0"
```

#### Configuración de Logging
```python
log_level: str = "INFO"
log_format: Optional[str] = None
log_handlers: Optional[List[str]] = None
log_file: Optional[str] = None
```

#### Configuración de Procesamiento
```python
processing_timeout: int = 30
max_response_length: Optional[int] = None
batch_size: int = 10
```

#### Configuración de API
```python
api_key: Optional[str] = None
api_base_url: Optional[str] = None
api_version: Optional[str] = None
```

#### Características y Modificadores
```python
feature_flags: Optional[Dict[str, bool]] = None
debug_mode: bool = False
```

### Métodos de Carga

#### from_dict
```python
@classmethod
def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config'
```
Carga configuración desde un diccionario.

**Ejemplo:**
```python
config_data = {
    "name": "MiAsistente",
    "log_level": "DEBUG",
    "api_key": "secret-key-123"
}
config = Config.from_dict(config_data)
```

#### from_env
```python
@classmethod
def from_env(cls, env_file: Optional[str] = None) -> 'Config'
```
Carga configuración desde variables de entorno o archivo .env.

**Parámetros:**
- `env_file` (opcional): Ruta al archivo .env

**Ejemplo:**
```python
# Desde variables de entorno
config = Config.from_env()

# Desde archivo específico
config = Config.from_env(".env.production")
```

#### from_yaml
```python
@classmethod
def from_yaml(cls, yaml_file: str) -> 'Config'
```
Carga configuración desde un archivo YAML.

**Ejemplo:**
```python
config = Config.from_yaml("config.yaml")
```

#### from_environ
```python
@classmethod
def from_environ(cls, prefix: str = "ASSISTANT_") -> 'Config'
```
Carga configuración desde variables de entorno con un prefijo específico.

**Parámetros:**
- `prefix`: Prefijo para las variables de entorno (por defecto: "ASSISTANT_")

**Ejemplo:**
```python
# Variables como ASSISTANT_NAME, ASSISTANT_LOG_LEVEL
config = Config.from_environ()
```

### Métodos de Validación

#### validate_api_key
```python
@validator('api_key')
def validate_api_key(cls, v):
    if v is not None and len(v) < 10:
        raise ValueError('api_key must be at least 10 characters')
    return v
```

#### validate_log_level
```python
@validator('log_level')
def validate_log_level(cls, v):
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if v.upper() not in valid_levels:
        raise ValueError(f'log_level must be one of {valid_levels}')
    return v.upper()
```

### Clase ConfigLoader

`ConfigLoader` es una utilidad para cargar configuración desde múltiples orígenes con sistema de prioridades.

#### Constructor
```python
def __init__(self, default_config: Optional[Config] = None):
```

#### Método Principal

```python
def load_config(
    self,
    config_dict: Optional[Dict[str, Any]] = None,
    env_file: Optional[str] = None,
    yaml_file: Optional[str] = None,
    env_prefix: str = "ASSISTANT_",
    use_environ: bool = True,
    override_with: Optional[Dict[str, Any]] = None
) -> Config
```

**Parámetros:**
- `config_dict`: Diccionario de configuración
- `env_file`: Archivo .env para cargar
- `yaml_file`: Archivo YAML para cargar
- `env_prefix`: Prefijo para variables de entorno
- `use_environ`: Si se deben usar variables de entorno
- `override_with`: Diccionario para sobreescribir valores finales

**Prioridad (de menor a mayor):**
1. Configuración por defecto
2. Diccionario de configuración
3. Archivo .env
4. Archivo YAML
5. Variables de entorno
6. Diccionario de sobreescritura final

**Ejemplo:**
```python
loader = ConfigLoader()

config = loader.load_config(
    env_file=".env.development",
    env_prefix="OSVALDO_",
    use_environ=True,
    override_with={
        "log_level": "DEBUG"  # Siempre será DEBUG
    }
)
```

### Validación de Configuración

La clase `ConfigValidator` proporciona validación avanzada:

```python
class ConfigValidator:
    @staticmethod
    def validate_config(config: Config) -> bool:
        """Valida la configuración completa."""
        
    @staticmethod
    def get_validation_errors(config: Config) -> List[str]:
        """Obtiene lista de errores de validación."""
        
    @staticmethod
    def validate_required_fields(config: Config, required_fields: List[str]) -> bool:
        """Valida campos requeridos específicos."""
```

**Ejemplo:**
```python
from assistant.core.config_validator import ConfigValidator

# Validar configuración
errors = ConfigValidator.get_validation_errors(config)
if errors:
    print(f"Errores de configuración: {errors}")
    raise ValueError("Configuración inválida")

# Validar campos requeridos
is_valid = ConfigValidator.validate_required_fields(
    config, 
    required_fields=["api_key", "name"]
)
```

### Gestión de Secretos

Para datos sensibles como API keys y contraseñas:

```python
from assistant.core.secret_manager import SecretManager

secret_manager = SecretManager()

# Encriptar un secreto
encrypted_key = secret_manager.encrypt("my-secret-key")

# Desencriptar un secreto
original_key = secret_manager.decrypt(encrypted_key)

# Guardar en configuración de forma segura
config = Config(api_key=encrypted_key, use_encrypted_secrets=True)
```

### Ejemplos de Uso

#### Configuración Básica
```python
from assistant import Config

config = Config(
    name="MiAsistente",
    log_level="INFO",
    processing_timeout=60
)
```

#### Configuración Multi-fuente
```python
from assistant.core.config_loader import ConfigLoader

loader = ConfigLoader()

config = loader.load_config(
    env_file=".env.production",
    use_environ=True
)
```

#### Configuración por Entorno
```python
# Archivo .env
ASSISTANT_NAME=ProductionBot
ASSISTANT_LOG_LEVEL=ERROR
ASSISTANT_API_KEY=sk-production-key
ASSISTANT_FEATURE_FLAGS='{"enable_analytics": true}'

# Código Python
config = Config.from_environ()
```

#### Configuración YAML
```python
# config.yaml
name: "YamlAssistant"
log_level: "DEBUG"
api_key: "sk-yaml-key"
processing_timeout: 120
feature_flags:
  enable_cache: true
  enable_metrics: false
  rate_limit: 100

# Código Python
config = Config.from_yaml("config.yaml")
```

### Configuración por Entorno con Priority Override

```python
from assistant.core.config_loader import ConfigLoader

# Sistema de prioridades de configuración
loader = ConfigLoader()

config = loader.load_config(
    config_dict={
        "name": "DefaultName",  # Baja prioridad
        "log_level": "INFO"
    },
    env_file=".env",  # Media prioridad, sobreescribe defaults
    override_with={
        "log_level": "DEBUG",  # Alta prioridad, siempre DEBUG
        "debug_mode": True     # Solo override puede establecer esto
    }
)

print(config.name)       # Del .env
print(config.log_level)  # "DEBUG" (del override)
print(config.debug_mode) # True (del override)
```

### Validación de Configuración

```python
from pydantic import ValidationError

try:
    config = Config(
        log_level="INVALID",  # Nivel inválido
        api_key="short"       # API key muy corta
    )
except ValidationError as e:
    print(f"Error de validación: {e}")
    
    # Corregir los errores
    config = Config(
        log_level="INFO",
        api_key="sk-valid-api-key"
    )
```