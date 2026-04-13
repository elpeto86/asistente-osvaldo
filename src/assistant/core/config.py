"""Configuration management for the assistant framework."""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import os
import yaml
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv


class Config(BaseModel):
    """Main configuration class for assistant framework."""
    
    # Core settings
    assistant_name: str = Field(default="Osvaldo", description="Name of the assistant")
    version: str = Field(default="0.1.0", description="Assistant version")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_handlers: List[str] = Field(default=["console"], description="Log handlers")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # API settings
    api_base_url: Optional[str] = Field(default=None, description="API base URL")
    api_key: Optional[str] = Field(default=None, description="API key")
    model_name: Optional[str] = Field(default=None, description="Model name")
    max_tokens: int = Field(default=1000, description="Maximum tokens")
    temperature: float = Field(default=0.7, description="Temperature parameter")
    
    # Performance settings
    request_timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retries")
    
    # Environment
    environment: str = Field(default="development", description="Environment name")
    
    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()
    
    @validator("temperature")
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError("temperature must be between 0 and 2")
        return v
    
    @validator("max_tokens")
    def validate_max_tokens(cls, v):
        if v <= 0:
            raise ValueError("max_tokens must be positive")
        return v
    
    class ModelConfig:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
    
    @classmethod
    def from_env(cls, env_file: str = ".env") -> "Config":
        """Load configuration from .env file."""
        load_dotenv(env_file)
        return cls()
    
    @classmethod
    def from_environ(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls()
    
    @classmethod
    def from_yaml(cls, yaml_file: Union[str, Path]) -> "Config":
        """Load configuration from YAML file."""
        yaml_path = Path(yaml_file)
        if not yaml_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {yaml_file}")
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """Load configuration from dictionary."""
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.dict()
    
    def to_yaml(self, yaml_file: Union[str, Path]) -> None:
        """Save configuration to YAML file."""
        yaml_path = Path(yaml_file)
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)