# Directrices de Contribución

Este documento describe cómo contribuir al proyecto Asistente Osvaldo. Si desea ayudar a mejorar el framework, siga estas directrices.

## Nuestros Valores

- **Código Limpio**: Escribir código que sea fácil de leer, mantener y extender
- **Diseño Intuitivo**: Crear APIs que sean naturales y predecibles
- **Documentación Completa**: Mantener una documentación actualizada y accesible
- **Testing Exhaustivo**: Garantizar la fiabilidad a través de pruebas automáticas
- **Colaboración Respetuosa**: Fomentar un ambiente inclusivo para todos los contribuidores

## Tipos de Contribuciones

### 1. Reportar Issues

- **Bugs**: Problemas que impiden el funcionamiento correcto
- **Features**: Sugerencias para mejorar o añadir funcionalidad
- **Documentación**: Mejoras en los documentos y ejemplos
- **Performance**: Optimización de rendimiento o uso de recursos

### 2. Propuestas de Cambio

Antes de iniciar desarrollo significativo, cree un issue para discutir la propuesta. Esto incluye:

- Cambios de arquitectura
- Nuevos módulos principales
- Cambios backwards-incompatible
- Grandes refactorizaciones

### 3. Código

- **Correcciones de bugs**: Pequeñas mejoras o arreglos
- **Nuevas funcionalidades**: Implementación de features propuestas
- **Refactorización**: Mejorar estructuras existentes sin cambiar comportamiento
- **Testing**: Aumentar coverage y robustez de tests
- **Documentación**: Actualizar y extender documentación

## Flujo de Trabajo

### 1. Preparación

```bash
# Fork del repositorio (en GitHub)
# Clonar su fork
git clone https://github.com/USUARIO/asistente-osvaldo.git
cd asistente-osvaldo

# Agregar upstream
git remote add upstream https://github.com/elpeto86/asistente-osvaldo.git

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o
.\venv\Scripts\activate  # Windows

# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt
pip install -e .

# Instalar pre-commit hooks
pre-commit install
```

### 2. Crear Rama

```bash
# Actualizar main
git checkout main
git pull upstream main

# Crear rama nueva
git checkout -b issue/numero-descripcion

# Ejemplos:
# git checkout -b issue/123-add-logging-utility
# git checkout -b fix/456-memory-leak
```

### 3. Desarrollo

Las ramas deben seguir esta convención de nombres:

**Features:** `feature/descripción-concisa`
- `feature/user-authentication`
- `feature/json-logging`
- `feature/config-validation`

**Fixes:** `fix/descripción-del-problema`
- `fix/memory-leak-assistant`
- `fix/config-loading-error`
- `fix/validation-bug`

**Documentation:** `docs/sección-actualizada`
- `docs/api-logging`
- `docs/configuration-guide`
- `docs/troubleshooting`

**Chore:** `chore/tarea-mantenimiento`
- `chore/update-dependencies`
- `chore/clean-up-tests`
- `chore/improve-ci`

### 4. Commit

Usar mensajes de commit claros y estandarizados:

```
<tipo>(<alcance>): <descripción>

[opcionalmente, body con más detalles]

[opcionalmente, footer con issue referenciado]
```

**Tipos permitidos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formateo, sin cambios lógicos
- `refactor`: Cambios que no son features ni fixes
- `test`: Agregar o actualizar tests
- `chore`: Tareas de mantenimiento, actualización de dependencias

**Ejemplos:**

```
feat(logging): add structured JSON logger

Implementa el nuevo sistema de logging estructurado que permite
generar logs en formato JSON con metadata enriquecida para mejor
analítica y debugging.

Closes #123
```

```
fix(core): resolve config loading with special characters

Arregla error cuando los archivos de configuración contienen
caracteres especiales como acentos o ñ en valores de string.

Fixes #456
```

### 5. Testing

Toda nueva funcionalidad debe incluir:

1. **Tests Unitarios**: Para cada nueva función/método
2. **Tests de Integración**: Para interacciones entre componente
3. **Tests de Edge Cases**: Escenarios límite y manejo de errores
4. **Documentación**: Docstrings o comentarios complejos

**Mínima cobertura**: 80% para nuevos archivos

```bash
# Verificar coverage
pytest --cov=src/assistant --cov-report=term-missing

# Asegurar que todos los tests pasan
pytest -vv

# Tests específicos del nuevo feature
pytest tests/unit/test_nuevo_modulo.py -v
```

### 6. Pre-commit y Linting

```bash
# Pre-commit hooks automático
git commit -m "feat: nueva funcionalidad"
# Los hooks se ejecutan automáticamente

# Ejecución manual si es necesario
pre-commit run --all-files
```

**Checks pre-commit:**
- Formato con Black
- Orden de importaciones con isort
- Linting con flake8
- Type checking con mypy
- Simple checks de commit

### 7. Pull Request

**Crear PR desde GitHub con:**

1. Título claro siguiendo convención de commits
2. Descripción detallada con:
   - Qué cambia y por qué
   - Cómo probar los cambios
   - Dependencies afectadas
   - Screenshots si aplica a UI

3. Tests automatizados pasarán
4. Revisión de código requerida

**Checklist para PR:**

- [ ] El código sigue PEP8 y las guías de estilo del proyecto
- [ ] Hay tests cubriendo la nueva funcionalidad
- [ ] Los tests nuevos pasan (pytest)
- [ ] El coverage de código es ≥80%
- [ ] La documentación está actualizada
- [ ] Los pre-commit hooks pasan
- [ ] El código es backwards compatible (si aplica)
- [ ] No hay side effects no deseados
- [ ] El mensaje de commit es claro y sigue convenciones

## Guías de Estilo

### Python

**PEP8 + Black Formatting:**
```python
# Black formatea con 88 caracteres por línea
# Buen formato
def process_message(
    message: UserMessage,
    config: Config,
    additional_params: Optional[Dict[str, Any]] = None,
) -> AssistantResponse:
    """Procesa un mensaje con configuración y parámetros opcionales."""
    return AssistantResponse(
        content=f"Processed: {message.content}",
        confidence=0.9
    )
```

**Docstrings según Google Style:**
```python
def calculate_metrics(data: List[float]) -> Dict[str, float]:
    """Calcula métricas estadísticas básicas de un conjunto de datos.

    Args:
        data: Lista de valores numéricos para análisis.

    Returns:
        Diccionario con métricas calculadas:
        - 'mean': Promedio de los valores
        - 'median': Mediana
        - 'std_dev': Desviación estándar

    Raises:
        ValueError: Si la lista está vacía o contiene valores no numéricos.
    """
```

**Type hints obligatorios:**
```python
from typing import List, Dict, Optional, Union, Any

def process_items(
    items: List[Dict[str, Any]],
    config: Dict[str, str]
) -> Optional[List[str]]:
    """Procesa items con configuración."""
    pass
```

### Guías de Archivo

**Estructura estándar:**
```python
"""Breve descripción del módulo (una línea).

Descripción más detallada del propósito y uso del módulo.
Incluir ejemplos si aplica.

Ejemplo:
    >>> from assistant.core import my_module
    >>> result = my_module.process_data([1, 2, 3])
    >>> print(result)
    {'mean': 2.0, 'count': 3}
"""

# Imports estándar primero
import os
import sys
from typing import Any

# Imports de terceros
import requests
from pydantic import BaseModel

# Imports locales
from assistant.core import config
from assistant.interfaces.base import BaseInterface

# Constants
DEFAULT_TIMEOUT = 30
API_VERSION = "v1"

# Classes and functions

logger = get_logger(__name__)
```

## Testing

### Principios

1. **AAA Pattern**: Arrange, Act, Assert
2. **Un test por concepto**: Cada test prueba una cosa
3. **Nombres descriptivos**: Use nombre que describa lo que testing
4. **Testing de errores**: Probar que los errores ocurran correctamente
5. **Boundary testing**: Probar valores límite

### Ejemplo de Test

```python
import pytest
from unittest.mock import Mock, patch
from assistant.core import MyModule


class TestMyModule:
    """Tests para el módulo de ejemplo."""
    
    def setup_method(self):
        """Setup antes de cada test."""
        self.config = {"timeout": 30}
        self.module = MyModule(self.config)
    
    def test_process_valid_input_success(self):
        """Test procesamiento con entrada válida."""
        # Arrange
        input_data = {"value": "test"}
        expected = {"result": "processed_test"}
        
        # Act
        result = self.module.process(input_data)
        
        # Assert
        assert result == expected
        assert "result" in result
    
    def test_process_invalid_input_raises_error(self):
        """Test que se lanza error con entrada inválida."""
        # Arrange
        invalid_input = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Input cannot be None"):
            self.module.process(invalid_input)
    
    @patch('assistant.core.external_api')
    def test_external_integration(self, mock_api):
        """Test integración con API externa."""
        # Arrange
        mock_api.call.return_value = {"status": "ok"}
        
        # Act
        result = self.module.call_external()
        
        # Assert
        assert result["status"] == "ok"
        mock_api.call.assert_called_once_with(expected_params)
    
    @pytest.mark.parametrize(
        "input_value,expected_output",
        [
            ("hello", "HELLO"),
            ("world", "WORLD"),
            ("123", "123")  # Edge case: numbers unchanged
        ]
    )
    def test_uppercase_various_inputs(self, input_value, expected_output):
        """Test uppercase con diferentes tipos de entrada."""
        result = self.module.uppercase(input_value)
        assert result == expected_output
```

## Documentación

### Docstrings

- **Todos los módulos** deben tener docstrings de módulo
- **Todas las clases públicas** deben tener docstrings
- **Todas las funciones/métodos públicos** deben tener docstrings
- **Parser/conversión automática** usa estos para generar API docs

### Ejemplos y Tutoriales

- Todo feature nuevo debe tener un ejemplo
- Los ejemplos deben ser copy-paste ejecutables
- Documentar ejemplos en `docs/examples/`

### Actualización de Changelog

El archivo `CHANGELOG.md` debe actualizarse con cada versión y major feature:

```markdown
## [1.2.0] - 2023-03-15

### Added
- Structured logging with JSON output (#123) by @contributor

### Changed
- Improve configuration loading performance (#456) by @contributor

### Fixed
- Memory leak in long-running sessions (#789) by @contributor

### Deprecated
- Old logging API will be removed in v2.0
```

## Manejo de Issues

### Reportar Bug

1. **Buscar primero**: Verificar que no exista
2. **Título claro**: Describe el problema específicamente
3. **Reproducible**: Pasos exactos para reproducir
4. **Entorno**: OS, Python version, dependencias
5. **Expected vs Actual**: Comportamiento esperado vs actual
6. **Logs/Mensajes**: Incluir mensajes de error completos

### Sugerir Feature

1. **Problema a resolver**: Qué problema resuelve el feature
2. **Propuesta detallada**: Cómo debería funcionar
3. **Casos de uso**: Quiénes lo usarían y cómo
4. **Alternativas consideradas**: Por qué esta solución
5. **Impacto**: Qué cambios implicaría

## Comunidad y Coordinación

### Labels de Issues

- `bug`: Errors o comportamiento incorrecto
- `enhancement`: Mejoras a funcionalidad existente
- `feature request`: Nueva funcionalidad
- `documentation`: Mejoras a docs
- `help wanted`: Buscando contribuidores
- `good first issue**: Ideal para nuevos contribuidores
- `priority: high/critical/low`

### Revisión de Código

**Para reviewers:**

- Ser constructivo y respetuoso
- Explicar *por qué* algo necesita cambio
- Aceptar diferentes estilos si funcionan
- Priorizar seguridad, performance y mantenibilidad

**Para autores:**

- Estar abierto a feedback
- Explicar decisiones complejas
- Aprender de revisiones anteriores
- Agradecer el tiempo de los reviewers

### Comunicación

- **Recomendado**: Usar inglés para issues y PRs para alcance internacional
- **Opcional**: Español en discusiones informales si todos están cómodos
- **Tono**: Profesional, inclusivo y colaborativo
- **Patience**: Dar tiempo para reviews y respuestas

## Manejo Conflictos

### Revisión De Decisions

Si desacuerdo sobre una propuesta:

1. **Crear issue** para discusión
2. **Presentar alternativas** con pros/contras
3. **Buscar consenso** antes de implementar
4. **Consultar maintainers** para decisión final

### Resolución de Merge Conflicts

```bash
# Actualizar rama main
git checkout main
git pull upstream main

# Volver a rama de feature
git checkout mi-feature
git rebase main

# Resolver conflicts manualmente y continuar
git add . 
git rebase --continue

# Forzar push (siempre con cuidado)
git push --force-with-lease origin mi-feature
```

## Reconocimiento

### Contribuidores

- Mantenemos `AUTHORS.md` con lista de contribuidores
- Cada PR merges agrega automáticamente nombre
- Releases agradecen a contribuidores importantes

### Mantainers

- **@elpeto86**: Project lead, architecture decisions
- Mantainers adicionales basados en contribución consistente

---

Gracias por considerar contribuir al Asistente Osvaldo. Tu ayuda hace este framework mejor para todos! 🚀