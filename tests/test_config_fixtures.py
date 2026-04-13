"""Configuration fixtures and test configurations."""

import os
from pathlib import Path
from typing import Any, Dict, Optional


@pytest.fixture
def test_config():
    """Provide a test configuration dictionary."""
    return {
        "assistant": {
            "name": "test-assistant",
            "version": "0.1.0",
            "description": "Test assistant instance",
            "debug": True
        },
        "logging": {
            "level": "DEBUG",
            "format": "simple",
            "handlers": ["console"],
            "file_path": None
        },
        "api": {
            "base_url": "https://api.test.com",
            "key": "test-api-key-123",
            "timeout": 30,
            "retry_attempts": 3
        },
        "database": {
            "url": "sqlite:///test.db",
            "pool_size": 5,
            "echo": False
        },
        "features": {
            "caching": False,
            "metrics": False,
            "tracing": False
        }
    }


@pytest.fixture
def minimal_config():
    """Provide a minimal configuration for basic testing."""
    return {
        "assistant": {
            "name": "minimal-assistant",
            "version": "0.1.0"
        },
        "logging": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }


@pytest.fixture
def production_config():
    """Provide a production-like configuration for testing."""
    return {
        "assistant": {
            "name": "prod-assistant",
            "version": "1.0.0",
            "description": "Production assistant",
            "debug": False
        },
        "logging": {
            "level": "WARNING",
            "format": "json",
            "handlers": ["file", "sentry"],
            "file_path": "/var/log/assistant/app.log"
        },
        "api": {
            "base_url": "https://api.production.com",
            "key": "prod-api-key-456",
            "timeout": 60,
            "retry_attempts": 5
        },
        "database": {
            "url": "postgresql://user:pass@db:5432/assistant",
            "pool_size": 20,
            "echo": False
        },
        "features": {
            "caching": True,
            "metrics": True,
            "tracing": True
        }
    }


@pytest.fixture
def invalid_config():
    """Provide an invalid configuration for error testing."""
    return {
        "assistant": {
            # Missing required fields
            "description": "Invalid config"
        },
        "logging": {
            "level": "INVALID_LEVEL",  # Invalid log level
            "handlers": ["invalid_handler"]  # Invalid handler
        },
        "api": {
            "base_url": "not-a-url",  # Invalid URL
            "timeout": -1  # Invalid timeout
        }
    }


@pytest.fixture
def config_files(tmp_path: Path, test_config: Dict[str, Any]):
    """Create configuration files for testing."""
    # Create .env file
    env_file = tmp_path / ".env"
    env_content = """
ASSISTANT_NAME=env-assistant
ASSISTANT_VERSION=0.1.0
LOG_LEVEL=INFO
API_BASE_URL=https://api.env.com
API_KEY=env-api-key-789
DATABASE_URL=postgresql://localhost/env_test
    """
    env_file.write_text(env_content.strip())
    
    # Create JSON config file
    json_file = tmp_path / "config.json"
    json_file.write_text(json.dumps(test_config, indent=2))
    
    # Create YAML config file
    yaml_file = tmp_path / "config.yaml"
    yaml_content = f"""
assistant:
  name: yaml-assistant
  version: 0.1.0
  description: Args: {test_config['assistant']['description']}
  debug: true

logging:
  level: DEBUG
  format: structured
  handlers:
    - console
    - file
  file_path: /tmp/yaml.log

api:
  base_url: https://api.yaml.com
  key: yaml-api-key-abc
  timeout: 45
  retry_attempts: 4

database:
  url: sqlite:///yaml_test.db
  pool_size: 10
    """
    yaml_file.write_text(yaml_content.strip())
    
    return {
        "env": env_file,
        "json": json_file,
        "yaml": yaml_file
    }


@pytest.fixture
def config_with_secrets():
    """Provide a configuration with secret values for testing."""
    return {
        "assistant": {
            "name": "secret-assistant",
            "version": "0.1.0"
        },
        "api": {
            "base_url": "https://api.secret.com",
            "key": "secret-key-do-not-log",
            "token": "Bearer token123",
            "certificate": "-----BEGIN CERTIFICATE-----\ntest_cert_data\n-----END CERTIFICATE-----"
        },
        "database": {
            "url": "postgresql://user:secret_pass@localhost/test",
            "password": "database_secret"
        },
        "secrets": {
            "jwt_key": "jwt_secret_key",
            "encryption_key": "encryption_secret_256bits"
        }
    }


@pytest.fixture
def environment_config(monkeypatch):
    """Set up environment variables for configuration testing."""
    env_vars = {
        "ASSISTANT_NAME": "env-test-assistant",
        "ASSISTANT_VERSION": "2.0.0",
        "ASSISTANT_DEBUG": "true",
        "LOG_LEVEL": "WARNING",
        "API_BASE_URL": "https://api.environment.com",
        "API_KEY": "env-provided-key-999",
        "API_TIMEOUT": "90",
        "DATABASE_URL": "postgresql://envuser:envpass@localhost/envtest",
        "CONFIG_FILE": "/tmp/env_config.json"
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    
    return env_vars


@pytest.fixture
def profile_configs(tmp_path: Path):
    """Create different configuration profiles."""
    # Development profile
    dev_config = {
        "assistant": {
            "name": "dev-assistant",
            "version": "0.1.0-dev",
            "debug": True
        },
        "logging": {
            "level": "DEBUG",
            "handlers": ["console"]
        },
        "database": {
            "url": "sqlite:///dev.db",
            "echo": True
        }
    }
    
    # Testing profile
    test_config = {
        "assistant": {
            "name": "test-assistant",
            "version": "0.1.0-test"
        },
        "logging": {
            "level": "ERROR",
            "handlers": []
        },
        "database": {
            "url": "sqlite:///:memory:"
        }
    }
    
    # Staging profile
    staging_config = {
        "assistant": {
            "name": "staging-assistant",
            "version": "1.0.0-rc1",
            "debug": False
        },
        "logging": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "file_path": "/var/log/staging.log"
        },
        "api": {
            "base_url": "https://api.staging.com"
        }
    }
    
    configs = {
        "development": dev_config,
        "testing": test_config,
        "staging": staging_config
    }
    
    # Write config files
    config_files = {}
    for profile, config in configs.items():
        config_path = tmp_path / f"{profile}.yaml"
        config_path.write_text(yaml.dump(config))
        config_files[profile] = config_path
    
    return config_files


@pytest.fixture
def config_validation_cases():
    """Provide various configurations for validation testing."""
    return {
        "valid_minimal": {
            "assistant": {
                "name": "valid",
                "version": "1.0.0"
            }
        },
        "valid_full": {
            "assistant": {
                "name": "full-assistant",
                "version": "1.0.0",
                "description": "A fully specified configuration",
                "debug": True
            },
            "logging": {
                "level": "DEBUG",
                "format": "json",
                "handlers": ["console", "file"]
            },
            "api": {
                "base_url": "https://api.example.com",
                "key": "test-key",
                "timeout": 30
            }
        },
        "invalid_missing_required": {
            "logging": {
                "level": "INFO"
            }
        },
        "invalid_wrong_types": {
            "assistant": {
                "name": 123,  # Should be string
                "version": "1.0.0",
                "debug": "yes"  # Should be boolean
            },
            "api": {
                "timeout": "fast"  # Should be number
            }
        },
        "invalid_values": {
            "logging": {
                "level": "INVALID",  # Not in valid levels
                "handlers": ["console", "invalid_handler"]
            }
        }
    }