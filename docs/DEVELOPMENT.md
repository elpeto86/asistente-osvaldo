# Guía de Desarrollo

Esta guía contiene instrucciones detalladas para configurar el entorno de desarrollo y trabajar con el framework Asistente Osvaldo.

## Requisitos Previos

### Sistema Operativo
- Windows 10 (con PowerShell o WSL2)
- macOS 10.15+ 
- Linux (Ubuntu 18.04+, CentOS 7+)

### Python
- Python 3.8+ (recomendado 3.9 o 3.10)
- pip 21.0+
- setuptools 57.0+
- wheel 0.37+

### Herramientas de Desarrollo
- Git 2.30+
- Editor de código (VS Code, PyCharm, o similar)
- Terminal/Shell con soporte para comandos Unix

## Configuración del Entorno

### 1. Clonar el Repositorio

```bash
git clone https://github.com/elpeto86/asistente-osvaldo.git
cd asistente-osvaldo
```

### 2. Crear Entorno Virtual

**Opción A: Usando venv (recomendado)**
```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
.\venv\Scripts\activate

# Activar (macOS/Linux)
source venv/bin/activate
```

**Opción B: Usando conda**
```bash
# Crear entorno
conda create -n osvaldo python=3.9

# Activar
conda activate osvaldo
```

**Opción C: Usando virtualenv**
```bash
# Instalar y crear entorno
pip install virtualenv
virtualenv venv

# Activar
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows
```

### 3. Instalar Dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Instalación para desarrollo
pip install -r requirements-dev.txt

# Instalación para producción
pip install -r requirements.txt

# Modo de desarrollo (editable)
pip install -e .
```

### 4. Configurar Pre-commit Hooks

```bash
# Inicializar pre-commit
pre-commit install

# Ejecutar hooks en todos los archivos
pre-commit run --all-files
```

### 5. Verificar Configuración

```bash
# Ejecutar tests para verificar configuración
pytest

# Verificar imports
python -c "import assistant; print('✓ Imports OK')"

# Verificar version de Python
python --version
```

## Configuración del编辑器

### VS Code

**Extensiones recomendadas:**
- Python (Microsoft)
- Pylance (Microsoft)
- Black Formatter (Microsoft)
- isort (Kevin Rose)
- Python Docstring Generator (Nils Werner)
- GitLens (GitKraken)

**Configuración workspace (`.vscode/settings.json`):**
```json
{
  "python.defaultInterpreterPath": "./venv/Scripts/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.mypyEnabled": true,
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true
  }
}
```

 launches (`.vscode/launch.json`):
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Main",
      "type": "python",
      "request": "launch",
      "program": "src/main.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "Python: Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "-vv",
        "--color=yes"
      ],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

### PyCharm

**Configuración recomendada:**
1. Abrir el proyecto
2. Configurar el intérprete Python a `venv`
3. Habilitar Tools > Black y Tools > isort
4. Configurar Code Style > Python
5. Configurar Settings > Tools > External Tools

## Estructura de Directorios

El proyecto sigue esta estructura estándar:

```
asistente-osvaldo/
├── src/                    # Código fuente principal
│   └── assistant/          # Package principal
│       ├── core/           # Componentes centrales
│       ├── interfaces/     # Interfaces y abstractos
│       ├── utils/          # Utilidades y helpers
│       └── plugins/        # Sistema de plugins
├── tests/                  # Tests y fixtures
│   ├── unit/              # Tests unitarios
│   ├── integration/       # Tests de integración
│   └── fixtures/          # Datos de prueba
├── docs/                  # Documentación
│   ├── api/               # Documentación API
│   └── examples/          # Ejemplos de uso
├── config/               # Archivos de configuración
├── scripts/              # Scripts de desarrollo y despliegue
├── .github/              # Configuración GitHub
├── .vscode/              # Configuración VS Code
├── .kilo/                # Configuración Kilo CLI
├── requirements*.txt      # Dependencias
├── pyproject.toml        # Configuración proyecto
├── pytest.ini           # Configuración pytest
├── mkdocs.yml            # Documentación
└── CHANGELOG.md          # Historial de cambios
```

## Flujo de Desarrollo

### 1. Crear Nueva Rama

```bash
# Actualizar main
git checkout main
git pull origin main

# Crear rama nueva
git checkout -b feature/nueva-funcionalidad

# O para corrección
git checkout -b fix/corregir-error
```

### 2. Desarrollo

**Escribir código siguiendo las convenciones:**

```python
# Estructura estándar de archivo
"""Módulo de ejemplo.

Este módulo proporciona funcionalidades X para el framework.

Ejemplo:
    >>> from assistant.core import ejemplo
    >>> ejemplo.mi_funcion()
    'resultado'

"""

from typing import Any, Dict, List
import logging

from assistant.interfaces.base import BaseInterface
from assistant.utils import get_logger

logger = get_logger(__name__)


class MiClase(BaseInterface):
    """Clase de ejemplo con implementación estándar."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializar clase con configuración.

        Args:
            config: Diccionario de configuración

        Raises:
            ValueError: Si la configuración es inválida
        """
        super().__init__()
        self.config = config
        self._validate_config()
    
    def mi_metodo(self, param: str) -> str:
        """Método de ejemplo.

        Args:
            param: Parámetro de entrada

        Returns:
            Resultado procesado
        """
        logger.debug("Procesando método", extra={"param": param})
        
        result = f"Procesado: {param}"
        
        logger.info(
            "Método completado",
            extra={
                "param_length": len(param),
                "result_length": len(result)
            }
        )
        
        return result
    
    def _validate_config(self) -> None:
        """Valida la configuración inicial."""
        required_fields = ['api_key', 'url']
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Falta campo requerido: {field}")
```

### 3. Formateo y Linting

```bash
# Formatear código
black src/ tests/
isort src/ tests/

# Linting
flake8 src/ tests/
pylint src/

# Type checking
mypy src/

# Pre-commit hooks ejecutan esto automáticamente
```

### 4. Testing

**Estructura de tests:**
```python
# tests/unit/test_mi_modulo.py
import pytest
from unittest.mock import Mock, patch

from assistant.core import MiClase


class TestMiClase:
    """Tests para MiClase."""
    
    def setup_method(self):
        """Setup antes de cada test."""
        self.config = {
            "api_key": "test_key",
            "url": "https://test.example.com"
        }
    
    def test_init_valid_config(self):
        """Test inicialización con configuración válida."""
        instance = MiClase(self.config)
        assert instance.config == self.config
    
    def test_init_invalid_config(self):
        """Test inicialización con configuración inválida."""
        invalid_config = {"invalid": "config"}
        with pytest.raises(ValueError, match="Falta campo requerido"):
            MiClase(invalid_config)
    
    def test_mi_metodo(self):
        """Test del método principal."""
        instance = MiClase(self.config)
        result = instance.mi_metodo("test_param")
        assert result == "Procesado: test_param"
    
    @patch('assistant.core.requests.get')
    def test_with_mock(self, mock_get):
        """Test con mock de API externa."""
        mock_get.return_value.json.return_value = {"status": "ok"}
        
        instance = MiClase(self.config)
        result = instance.call_external_api()
        
        assert result == {"status": "ok"}
        mock_get.assert_called_once_with("https://test.example.com")
```

**Ejecutar tests:**
```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=src/assistant --cov-report=html

# Tests específicos
pytest tests/unit/test_mi_modulo.py -v

# Por nombre
pytest -k "test_mi_metodo"

# Ver solo failures primero
pytest -x --ff
```

### 5. Commit y Push

```bash
# Verificar cambios
git status

# Agregar archivos
git add src/mi_modulo.py tests/unit/test_mi_modulo.py

# Commit
git commit -m "feat: agregar MI_MODULO con funcionalidad X

- Implementar clase MiClase con método principal
- Agregar tests unitarios con 95% coverage
- Actualizar documentación

Closes #123"

# Push
git push origin feature/nueva-funcionalidad

# Crear Pull Request desde GitHub/GitLab
```

## Configuración de Entornos

### Desarrollo Local

Archivo `.env.development`:
```env
# Configuración de desarrollo
ASSISTANT_NAME=OsvaldoDev
LOG_LEVEL=DEBUG
LOG_HANDLERS=console
API_BASE_URL=http://localhost:8000
ENABLE_RELOAD=true
```

### Staging

Archivo `.env.staging`:
```env
# Configuración de staging
ASSISTANT_NAME=OsvaldoStaging
LOG_LEVEL=INFO
API_BASE_URL=https://staging-api.example.com
ENVIRONMENT=staging
```

### Producción

Archivo `.env.production`:
```env
# Configuración de producción
ASSISTANT_NAME=Osvaldo
LOG_LEVEL=WARNING
API_BASE_URL=https://api.example.com
ENVIRONMENT=production
ENABLE_METRICS=true
RATE_LIMIT=1000
```

## Manejo de Problemas Comunes

### Errores de Imports

**Problema:** `ModuleNotFoundError`

**Solución:**
```bash
# Verificar estructura de directorios
ls -la src/

# Verificar PYTHONPATH (si está ejecutando fuera de venv)
echo $PYTHONPATH

# Instalar en modo editable
pip install -e .
```

### Problemas con Tests

**Problema:** Tests failing with import errors

**Solución:**
```bash
# Verificar que tests importen correctamente
python -c "import sys; print(sys.path)"

# Verificar pytest.ini
cat pytest.ini

# Limpiar cache
pytest --cache-clear
```

### Problemas con Pre-commit

**Problema:** Pre-commit hooks failing

**Solución:**
```bash
# Reinstalar pre-commit
pre uninstall pre-commit
pip install pre-commit
pre-commit install

# Bypass temporalmente (no recomendado)
git commit --no-verify
```

### Problemas de Formato

**Problema:** Formato inconsistente

**Solución:**
```bash
# Aplicar formato completo
black src/ tests/
isort src/ tests/

# Verificar configuración de Black
black --check src/

# Actualizar configuración si es necesario
black --line-length 100 src/  # Custom length
```

## Build y Despliegue

### Crear Distribution

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build wheel and source distribution
python -m build

# Check package
python -m twine check dist/*
```

### Publicar a PyPI

```bash
# Test PyPI
python -m twine upload --repository testpypi dist/*

# Production PyPI
python -m twine upload dist/*
```

### Deploy con Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY pyproject.toml ./

# Install application
RUN pip install -e .

# Run application
CMD ["python", "-m", "assistant.main"]
```

## Recursos Adicionales

### Documentación útil
- [Python Developer Guide](https://docs.python.org/3/devguide/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatting](https://black.readthedocs.io/)

### Herramientas recomendadas
- [Poetry](https://python-poetry.org/) para gestión de paquetes
- [tox](https://tox.readthedocs.io/) para testing multi-entorno
- [mypy](https://mypy.readthedocs.io/) para type checking
- [Sphinx](https://www.sphinx-doc.org/) para documentación

### Comunicación
- Crear issues en GitHub para bugs o feature requests
- Discusiones en GitHub para preguntas generales
- Contribuir siguiendo las directrices de CONTRIBUTING.md