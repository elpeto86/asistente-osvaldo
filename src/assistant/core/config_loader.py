"""Configuration loading utilities for multiple sources."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from .config import Config


def load_from_file(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    config_path = Path(config_path)
    
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file {config_path}: {e}")


def load_from_env(prefix: str = "ASSISTANT_") -> Dict[str, Any]:
    """Load configuration from environment variables with optional prefix."""
    config = {}
    
    for key, value in os.environ.items():
        if key.startswith(prefix):
            # Remove prefix and convert to lowercase
            config_key = key[len(prefix):].lower()
            
            # Convert underscores to dots for nested keys
            config_key = config_key.replace('_', '.')
            
            # Convert string values to appropriate types
            config[config_key] = _convert_env_value(value)
    
    return config


def _convert_env_value(value: str) -> Union[str, int, float, bool, list]:
    """Convert environment variable string to appropriate type."""
    # Handle boolean values
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'
    
    # Handle numeric values
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
    
    # Handle comma-separated lists
    if ',' in value:
        return [item.strip() for item in value.split(',')]
    
    # Handle JSON-like values
    if (value.startswith('{') and value.endswith('}')) or \
       (value.startswith('[') and value.endswith(']')):
        import json
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
    
    return value


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple configuration dictionaries."""
    result = {}
    
    for config in configs:
        result = _deep_merge(result, config)
    
    return result


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries with override taking precedence."""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def load_config_with_sources(
    config_file: Optional[Union[str, Path]] = None,
    env_prefix: str = "ASSISTANT_",
    create_directories: bool = True,
    **kwargs
) -> Config:
    """Load configuration from multiple sources in order of precedence."""
    
    # 1. Load from YAML config file (lowest precedence)
    file_config = {}
    if config_file:
        file_config = load_from_file(config_file)
    
    # 2. Load from environment variables
    env_config = load_from_env(env_prefix)
    
    # 3. Merge with explicit kwargs (highest precedence)
    explicit_config = kwargs
    
    # Merge all configs
    merged = merge_configs(file_config, env_config, explicit_config)
    
    # Validate values before creating Config
    flattened = flatten_dict(merged)
    
    # Create Config instance
    config = Config(**flattened)
    
    if create_directories:
        config.create_directories()
    
    return config


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary using dot notation."""
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


def save_config_to_file(config: Config, config_path: Union[str, Path]) -> None:
    """Save configuration to YAML file with sensitive values masked."""
    config_path = Path(config_path)
    
    # Get masked config to avoid saving sensitive data
    masked_config = config.mask_sensitive_values()
    
    # Convert to dictionary for YAML output
    config_dict = masked_config.dict()
    
    # Convert Path objects to strings
    def convert_paths(obj):
        if isinstance(obj, dict):
            return {k: convert_paths(v) for k, v in obj.items()}
        elif isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, list):
            return [convert_paths(item) for item in obj]
        else:
            return obj
    
    config_dict = convert_paths(config_dict)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)


def get_default_config_paths() -> list[Path]:
    """Get list of default configuration file locations to check."""
    current_dir = Path.cwd()
    config_dir = current_dir / "config"
    home_config = Path.home() / ".config" / "assistant"
    
    return [
        current_dir / "assistant.yml",
        current_dir / "assistant.yaml", 
        config_dir / "assistant.yml",
        config_dir / "assistant.yaml",
        home_config / "config.yml",
        home_config / "config.yaml"
    ]