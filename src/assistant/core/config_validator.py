"""Configuration validation utilities."""

from typing import Dict, Any, List, Optional, Set
import re
from pathlib import Path
from pydantic import ValidationError
from .config import Config


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigValidator:
    """Validates configuration values against requirements."""
    
    def __init__(self):
        self.validation_rules: Dict[str, List[callable]] = {}
        self.required_fields: Set[str] = set()
        self.required_environments: Dict[str, Set[str]] = {}
        
    def add_required_field(self, field_path: str, environments: Optional[List[str]] = None):
        """Add a required field validation.
        
        Args:
            field_path: Dot-separated path to the field (e.g., 'api_host')
            environments: List of environments where this field is required
        """
        if environments is None:
            environments = ['production', 'staging']
            
        self.required_fields.add(field_path)
        for env in environments:
            if env not in self.required_environments:
                self.required_environments[env] = set()
            self.required_environments[env].add(field_path)
    
    def add_validation_rule(self, field_path: str, validator_func: callable):
        """Add a custom validation rule for a field.
        
        Args:
            field_path: Dot-separated path to the field
            validator_func: Function that takes value and returns True/False or raises ValueError
        """
        if field_path not in self.validation_rules:
            self.validation_rules[field_path] = []
        self.validation_rules[field_path].append(validator_func)
    
    def validate(self, config: Config) -> List[str]:
        """Validate configuration and return list of errors.
        
        Args:
            config: Configuration instance to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check required fields
        errors.extend(self._validate_required_fields(config))
        
        # Apply custom validation rules
        errors.extend(self._validate_custom_rules(config))
        
        # Cross-field validation
        errors.extend(self._validate_cross_fields(config))
        
        return errors
    
    def _validate_required_fields(self, config: Config) -> List[str]:
        """Check required fields are present and not empty."""
        errors = []
        environment = config.environment
        
        # Get required fields for current environment
        required_for_env = self.required_environments.get(environment, set())
        always_required = self.required_fields - set().union(*self.required_environments.values())
        all_required = required_for_env | always_required
        
        for field_path in all_required:
            value = self._get_nested_value(config, field_path)
            
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"Required field '{field_path}' is missing or empty")
        
        return errors
    
    def _validate_custom_rules(self, config: Config) -> List[str]:
        """Apply custom validation rules."""
        errors = []
        
        for field_path, validators in self.validation_rules.items():
            value = self._get_nested_value(config, field_path)
            
            if value is not None:
                for validator in validators:
                    try:
                        if not validator(value):
                            errors.append(f"Validation failed for field '{field_path}'")
                    except ValueError as e:
                        errors.append(f"Validation failed for field '{field_path}': {str(e)}")
        
        return errors
    
    def _validate_cross_fields(self, config: Config) -> List[str]:
        """Validate cross-field dependencies."""
        errors = []
        
        # CORS validation
        if config.allowed_origins and not all(re.match(r'^https?://', origin) for origin in config.allowed_origins):
            errors.append("All allowed_origins must be valid URLs")
        
        # Rate limiting validation
        if config.rate_limit_enabled and config.rate_limit_requests <= 0:
            errors.append("rate_limit_requests must be greater than 0 when rate limiting is enabled")
        
        if config.rate_limit_enabled and config.rate_limit_window <= 0:
            errors.append("rate_limit_window must be greater than 0 when rate limiting is enabled")
        
        # Path validation
        if not config.base_path.exists():
            errors.append(f"base_path '{config.base_path}' does not exist")
        
        # Security validation for production
        if config.environment == 'production':
            if not config.secret_key or len(config.secret_key) < 32:
                errors.append("secret_key must be at least 32 characters in production")
            
            if config.debug:
                errors.append("debug mode should not be enabled in production")
        
        return errors
    
    def _get_nested_value(self, obj: Any, path: str) -> Any:
        """Get nested value using dot notation."""
        parts = path.split('.')
        value = obj
        
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value


def create_default_validator() -> ConfigValidator:
    """Create a validator with common validation rules."""
    validator = ConfigValidator()
    
    # Add required fields for production/staging
    validator.add_required_field('secret_key', ['production', 'staging'])
    validator.add_required_field('api_host', ['production', 'staging'])
    
    # Add custom validation rules
    def validate_port_range(port):
        if not isinstance(port, int) or not (1 <= port <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return True
    
    def validate_email_format(email):
        if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValueError("Invalid email format")
        return True
    
    def validate_url_format(url):
        if url and not re.match(r'^https?://', url):
            raise ValueError("URL must start with http:// or https://")
        return True
    
    def validate_worker_count(workers):
        if not isinstance(workers, int) or workers < 1:
            raise ValueError("Worker count must be a positive integer")
        return True
    
    validator.add_validation_rule('api_port', validate_port_range)
    validator.add_validation_rule('api_workers', validate_worker_count)
    validator.add_validation_rule('email', validate_email_format)  # if email is added
    
    # Validate each CORS origin is a URL
    def validate_cors_origins(origins):
        for origin in origins:
            if not re.match(r'^https?://', origin):
                raise ValueError("CORS origin must be a valid URL")
        return True
    
    validator.add_validation_rule('allowed_origins', validate_cors_origins)
    
    return validator


def validate_config(config: Config) -> None:
    """Validate configuration and raise exception if invalid.
    
    Args:
        config: Configuration to validate
        
    Raises:
        ConfigValidationError: If validation fails
    """
    validator = create_default_validator()
    errors = validator.validate(config)
    
    if errors:
        raise ConfigValidationError(f"Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors))


def validate_and_create_directories(config: Config) -> Config:
    """Validate configuration and create necessary directories.
    
    Args:
        config: Configuration to validate and use
        
    Returns:
        The validated config instance
        
    Raises:
        ConfigValidationError: If validation fails
    """
    validate_config(config)
    config.create_directories()
    return config


# Common validation functions that can be used in custom validators
def is_positive_number(value):
    """Check if value is a positive number."""
    return isinstance(value, (int, float)) and value > 0


def is_non_empty_string(value):
    """Check if value is a non-empty string."""
    return isinstance(value, str) and len(value.strip()) > 0


def is_valid_url(value):
    """Check if value is a valid URL."""
    return isinstance(value, str) and re.match(r'^https?://', value) is not None


def is_valid_email(value):
    """Check if value is a valid email address."""
    return isinstance(value, str) and re.match(r'^[^@]+@[^@]+\.[^@]+$', value) is not None


def is_in_range(min_val, max_val):
    """Create a validator that checks if value is in range."""
    def validator(value):
        if not isinstance(value, (int, float)):
            raise ValueError("Value must be a number")
        if not (min_val <= value <= max_val):
            raise ValueError(f"Value must be between {min_val} and {max_val}")
        return True
    return validator


def is_one_of(allowed_values):
    """Create a validator that checks if value is one of allowed values."""
    def validator(value):
        if value not in allowed_values:
            raise ValueError(f"Value must be one of: {allowed_values}")
        return True
    return validator