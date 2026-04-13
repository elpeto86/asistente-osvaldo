"""
Setup script for the assistant framework.

This setup.py provides backward compatibility with tools that still expect it.
The primary build configuration is in pyproject.toml.
"""

import os
from pathlib import Path
from setuptools import setup, find_packages

# Read version from __init__.py
version_file = Path(__file__).parent / "src" / "assistant" / "__init__.py"
version_vars = {}
if version_file.exists():
    with open(version_file, "r") as f:
        exec(f.read(), version_vars)
    VERSION = version_vars.get("__version__", "0.1.0")
else:
    VERSION = "0.1.0"

# Read long description from README
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as fh:
        LONG_DESCRIPTION = fh.read()
else:
    LONG_DESCRIPTION = "A modular Python framework for building AI assistants"

# Core dependencies
CORE_DEPS = [
    "pydantic>=2.5.0,<3.0.0",
    "pyyaml>=6.0.1,<7.0.0",
    "cryptography>=41.0.0,<42.0.0",
    "structlog>=23.2.0,<24.0.0",
]

# Optional dependencies
EXTRAS_REQUIRES = {
    "openai": ["openai>=1.0.0,<2.0.0"],
    "anthropic": ["anthropic>=0.7.0,<1.0.0"],
    "http": ["httpx>=0.25.0,<1.0.0"],
    "asyncio": ["aiofiles>=23.2.0,<24.0.0", "asyncio-mqtt>=0.11.0,<1.0.0"],
    "all": [
        "assistant-framework[openai,anthropic,http,asyncio]"
    ],
    "dev": [
        "pytest>=7.4.0,<8.0.0",
        "pytest-cov>=4.1.0,<5.0.0",
        "pytest-asyncio>=0.21.0,<1.0.0",
        "pytest-mock>=3.12.0,<4.0.0",
        "pytest-xdist>=3.3.0,<4.0.0",
        "black>=23.10.0,<24.0.0",
        "isort>=5.12.0,<6.0.0",
        "ruff>=0.1.0,<1.0.0",
        "mypy>=1.7.0,<2.0.0",
        "pre-commit>=3.5.0,<4.0.0",
        "ipython>=8.17.0,<9.0.0",
        "mkdocs>=1.5.0,<2.0.0",
        "mkdocs-material>=9.4.0,<10.0.0",
        "mkdocstrings[python]>=0.23.0,<1.0.0",
    ],
}

setup(
    name="assistant-framework",
    version=VERSION,
    description="A modular Python framework for building AI assistants",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Assistant Framework Team",
    author_email="team@assistant-framework.dev",
    maintainer="Assistant Framework Team",
    maintainer_email="team@assistant-framework.dev",
    url="https://github.com/assistant-framework/assistant-framework",
    project_urls={
        "Documentation": "https://assistant-framework.readthedocs.io",
        "Repository": "https://github.com/assistant-framework/assistant-framework.git",
        "Bug Tracker": "https://github.com/assistant-framework/assistant-framework/issues",
        "Changelog": "https://github.com/assistant-framework/assistant-framework/blob/main/CHANGELOG.md",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="ai assistant framework chatbot llm",
    python_requires=">=3.9",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "assistant": ["py.typed", "*.yaml", "*.yml"],
    },
    install_requires=CORE_DEPS,
    extras_require=EXTRAS_REQUIRES,
    entry_points={
        "console_scripts": [
            "assistant=assistant.cli:main",
        ],
    },
    zip_safe=False,
    platforms=["any"],
)