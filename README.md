# Asistente Osvaldo

Un framework modular de Python para construir asistentes de IA con una arquitectura bien definida, gestión de configuración segura y herramientas de prueba integrales.

## Características

- **Arquitectura modular**: Estructura clara con separación de responsabilidades
- **Gestión de configuración**: Sistema de configuración type-safe con Pydantic
- **Logging estructurado**: Múltiples manejadores (consola, archivo, JSON)
- **Framework de pruebas**: Configuración completa con pytest y utilidades
- **Sistema de plugins**: Arquitectura extensible
- **Type Safety**: Anotaciones de tipo completas en todo el código

## Estructura del Proyecto

```
asistente-osvaldo/
├── src/
│   └── assistant/
│       ├── core/           # Componentes principales del asistente
│       ├── interfaces/     # Interfaces y clases de mensajes
│       ├── utils/          # Utilidades y herramientas
│       └── plugins/        # Sistema de plugins extensible
├── tests/                  # Tests y fixtures
├── docs/                   # Documentación
├── config/                 # Archivos de configuración
└── scripts/                # Scripts de desarrollo
```

## Instalación

### Requisitos Previos

- Python 3.8+
- pip (o pipenv/venv para gestión de entornos)

### Instalación desde el Repositorio

```bash
git clone https://github.com/elpeto86/asistente-osvaldo.git
cd asistente-osvaldo
pip install -r requirements.txt
```

### Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar tests
pytest

# Formatear código
black src/ tests/
isort src/ tests/
```

## Uso Rápido

```python
from src.assistant import BaseAssistant, UserMessage, AssistantMessage, Config

# Configurar el asistente
config = Config(
    api_key="tu-api-key",
    model_name="gpt-3.5-turbo",
    log_level="INFO"
)

# Crear una implementación del asistente
class MiAsistente(BaseAssistant):
    async def process_input(self, message: UserMessage) -> AssistantMessage:
        # Implementa tu lógica aquí
        return AssistantMessage(
            content=f"Recibí: {message.content}",
            confidence=0.9
        )

# Usar el asistente
asistente = MiAsistente(config)
respuesta = await asistente.process_input(
    UserMessage(content="Hola, ¿cómo estás?")
)
print(respuesta.content)
```

## Configuración

El soporte para configuración multi-fuente incluye:

- Archivos `.env`
- Variables de entorno
- Archivos YAML
- Argumentos de línea de comandos

### Ejemplo de configuración

```python
from src.assistant import Config

# Desde archivo .env
config = Config.from_env(".env")

# Desde variables de entorno
config = Config.from_environ()

# Manualmente
config = Config(
    api_key="sk-...",
    model_name="gpt-4",
    max_tokens=1000,
    temperature=0.7
)
```

## Logging

El framework incluye un sistema de logging estructurado con múltiples manejadores:

```python
from src.assistant.utils import get_logger

# Logger para componentes específicos
logger = get_logger("mi_componente")
logger.info("Procesando solicitud", extra={"user_id": 123})
```

## Desarrollo

### Tests

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=src/assistant

# Tests específicos
pytest tests/test_config.py -v
```

### Linting

```bash
# Formatear
black src/ tests/
isort src/ tests/

# Lint
flake8 src/ tests/
mypy src/
```

## Plugins

El sistema de plugins permite extender la funcionalidad:

```python
from src.assistant.plugins import BasePlugin

class MiPlugin(BasePlugin):
    def initialize(self, config: Config) -> None:
        # Inicialización del plugin
        pass

    def process_message(self, message: UserMessage) -> UserMessage:
        # Procesamiento personalizado
        return message
```

## Arquitectura

### Componentes Principales

- **BaseAssistant**: Clase abstracta para implementaciones de asistentes
- **Config**: Gestión centralizada de configuración
- **Message System**: Tipos de mensajes estandarizados
- **Logging**: Sistema de logging estructurado
- **Testing**: Framework completo con fixtures

### Interfaces

```python
from src.assistant.interfaces import (
    UserMessage, AssistantMessage, SystemMessage,
    AssistantResponse, Message
)

# Crear mensajes
user_msg = UserMessage(content="Hola", user_id=123)
assistant_msg = AssistantMessage(content="¡Hola!", confidence=0.95)
system_msg = SystemMessage(content="Instrucción del sistema")
```

## Contribuir

1. Fork del proyecto
2. Crear un feature branch: `git checkout -b feature/nueva-funcionalidad`
3. Hacer commit de cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push al branch: `git push origin feature/nueva-funcionalidad`
5. Crear un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

- **Proyecto**: https://github.com/elpeto86/asistente-osvaldo
- **Email**: osvaldo@example.com
- **Issues**: https://github.com/elpeto86/asistente-osvaldo/issues