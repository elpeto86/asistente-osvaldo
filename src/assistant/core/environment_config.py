"""Environment-specific configuration management."""

from typing import Dict, Any, Optional, Union
from pathlib import Path
import os
from copy import deepcopy
from .config import Config
from .config_loader import (
    load_from_file, 
    load_from_env, 
    merge_configs, 
    get_default_config_paths
)
from .config_validator import validate_config


class EnvironmentConfig:
    """Manages environment-specific configurations."""
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """Initialize environment configuration manager.
        
        Args:
            base_path: Base path for configuration files
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.config_dir = self.base_path / "config"
        self.environments = ["development", "testing", "staging", "production"]
        
    def load_for_environment(
        self,
        environment: str,
        config_file: Optional[Union[str, Path]] = None,
        include_base: bool = True
    ) -> Config:
        """Load configuration for specific environment.
        
        Args:
            environment: Environment name (development, testing, staging, production)
            config_file: Override config file to use
            include_base: Whether to include base configuration
            
        Returns:
            Loaded valid configuration
        """
        if environment not in self.environments:
            raise ValueError(f"Unknown environment: {environment}. Must be one of: {self.environments}")
        
        # Load configurations in order of precedence
        configs = []
        
        # 1. Base configuration (common to all environments)
        if include_base:
            base_config = self._load_config_file("base")
            if base_config:
                configs.append(base_config)
        
        # 2. Environment-specific configuration
        env_config = self._load_config_file(environment)
        if env_config:
            configs.append(env_config)
        
        # 3. Override config file if provided
        if config_file:
            override_config = load_from_file(config_file)
            if override_config:
                configs.append(override_config)
        
        # 4. Environment variables (highest precedence)
        env_vars = load_from_env()
        if env_vars:
            configs.append(env_vars)
        
        # 5. Explicit environment setting
        configs.append({"environment": environment})
        
        # Merge all configurations
        merged = {}
        for config in configs:
            merged = merge_configs(merged, config)
        
        # Create and validate config
        config = Config(**merged)
        validate_config(config)
        
        return config
    
    def _load_config_file(self, name: str) -> Dict[str, Any]:
        """Load configuration file by name.
        
        Args:
            name: Configuration name (e.g., "base", "development", "production")
            
        Returns:
            Loaded configuration dictionary
        """
        # Try different file locations and extensions
        possible_files = [
            self.config_dir / f"{name}.yml",
            self.config_dir / f"{name}.yaml",
            self.base_path / f"{name}.yml",
            self.base_path / f"{name}.yaml",
            self.base_path / "config.yml",
            self.base_path / "config.yaml",
        ]
        
        for file_path in possible_files:
            if file_path.exists():
                return load_from_file(file_path)
        
        return {}
    
    def create_env_configs(self, base_config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Create environment-specific configs from base config.
        
        Args:
            base_config: Base configuration dictionary
            
        Returns:
            Dictionary of environment-specific configurations
        """
        configs = {}
        
        for env in self.environments:
            config = deepcopy(base_config)
            config["environment"] = env
            
            # Environment-specific overrides
            if env == "development":
                config.update({
                    "debug": True,
                    "log_level": "DEBUG",
                    "enable_metrics": False,
                    "enable_tracing": True,
                })
            elif env == "testing":
                config.update({
                    "debug": True,
                    "log_level": "DEBUG",
                    "enable_metrics": False,
                    "enable_tracing": False,
                    "rate_limit_enabled": False,
                })
            elif env == "staging":
                config.update({
                    "debug": False,
                    "log_level": "INFO",
                    "enable_metrics": True,
                    "enable_tracing": True,
                })
            elif env == "production":
                config.update({
                    "debug": False,
                    "log_level": "WARNING",
                    "enable_metrics": True,
                    "enable_tracing": True,
                    "enable_profiling": False,
                })
            
            configs[env] = config
        
        return configs
    
    def save_config_for_environment(
        self, 
        config: Config, 
        environment: str,
        output_file: Optional[Union[str, Path]] = None
    ) -> Path:
        """Save configuration for specific environment.
        
        Args:
            config: Configuration to save
            environment: Environment name
            output_file: Output file path (auto-generated if not provided)
            
        Returns:
            Path to saved file
        """
        if environment not in self.environments:
            raise ValueError(f"Unknown environment: {environment}")
        
        if output_file is None:
            self.config_dir.mkdir(exist_ok=True)
            output_file = self.config_dir / f"{environment}.yml"
        
        output_path = Path(output_file)
        
        # Import here to avoid circular imports
        from .config_loader import save_config_to_file, convert_paths
        save_config_to_file(config, output_path)
        
        return output_path
    
    def get_current_environment(self) -> str:
        """Detect current environment from various sources.
        
        Returns:
            Environment name
        """
        # 1. Check explicit environment variable
        if "ENVIRONMENT" in os.environ:
            env = os.environ["ENVIRONMENT"].lower()
            if env in self.environments:
                return env
        
        # 2. Check common environment variables
        env_vars = [
            "APP_ENV", "ENV", "NODE_ENV", "FLASK_ENV", "DJANGO_SETTINGS_MODULE"
        ]
        for var in env_vars:
            if var in os.environ:
                value = os.environ[var].lower()
                if "prod" in value:
                    return "production"
                elif "stag" in value:
                    return "staging"
                elif "test" in value:
                    return "testing"
                elif "dev" in value:
                    return "development"
        
        # 3. Default based on environment
        if os.environ.get("CI") == "true":
            return "testing"
        
        # 4. Default to development
        return "development"
    
    def list_config_files(self) -> Dict[str, Path]:
        """List available configuration files by environment.
        
        Returns:
            Dictionary mapping environment names to file paths
        """
        files = {}
        
        for env in self.environments:
            config_file = self._get_config_file_for_env(env)
            if config_file and config_file.exists():
                files[env] = config_file
        
        # Also check for base config
        base_file = self._get_config_file_for_env("base")
        if base_file and base_file.exists():
            files["base"] = base_file
        
        return files
    
    def _get_config_file_for_env(self, env: str) -> Optional[Path]:
        """Get configuration file path for environment."""
        possible_files = [
            self.config_dir / f"{env}.yml",
            self.config_dir / f"{env}.yaml",
            self.base_path / f"{env}.yml",
            self.base_path / f"{env}.yaml",
        ]
        
        for file_path in possible_files:
            if file_path.exists():
                return file_path
        
        return None
    
    def validate_config_for_environment(
        self, 
        config: Config, 
        expected_env: Optional[str] = None
    ) -> bool:
        """Validate configuration matches expected environment.
        
        Args:
            config: Configuration to check
            expected_env: Expected environment (auto-detected if not provided)
            
        Returns:
            True if valid for environment
        """
        if expected_env is None:
            expected_env = self.get_current_environment()
        
        # Check environment matches
        if config.environment != expected_env:
            return False
        
        # Environment-specific validation
        if config.environment == "production":
            # Production should not have debug mode
            if config.debug:
                return False
            
            # Should have required security settings
            if not config.secret_key or len(config.secret_key) < 32:
                return False
        
        elif config.environment == "development":
            # Development should be more permissive
            pass
        
        return True
    
    def create_sample_configs(self, output_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
        """Create sample configuration files for all environments.
        
        Args:
            output_dir: Output directory for sample configs
            
        Returns:
            Dictionary mapping environment names to created file paths
        """
        if output_dir is None:
            output_dir = self.config_dir
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(exist_ok=True)
        
        # Base configuration
        base_config = {
            "name": "my-assistant",
            "version": "0.1.0",
            "api_host": "localhost",
            "api_port": 8000,
            "log_level": "INFO",
            "enable_metrics": True,
            "enable_tracing": True,
        }
        
        # Generate configs for all environments
        env_configs = self.create_env_configs(base_config)
        
        created_files = {}
        
        for env, config in env_configs.items():
            file_path = output_dir / f"{env}.yml"
            
            import yaml
            with open(file_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            
            created_files[env] = file_path
        
        return created_files


# Convenience functions
def load_config_for_environment(
    environment: Optional[str] = None,
    config_file: Optional[Union[str, Path]] = None,
    base_path: Optional[Union[str, Path]] = None
) -> Config:
    """Load configuration for specific environment.
    
    Args:
        environment: Environment name (auto-detected if not provided)
        config_file: Override config file to use
        base_path: Base path for configuration files
        
    Returns:
        Loaded valid configuration
    """
    env_manager = EnvironmentConfig(base_path)
    
    if environment is None:
        environment = env_manager.get_current_environment()
    
    return env_manager.load_for_environment(environment, config_file)