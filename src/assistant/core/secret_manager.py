"""Secret management utilities for secure configuration handling."""

import os
import json
import hashlib
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class SecretManager:
    """Manages sensitive configuration values with encryption and masking."""
    
    def __init__(self, master_key: Optional[str] = None, secret_file: Optional[Union[str, Path]] = None):
        """Initialize secret manager.
        
        Args:
            master_key: Master key for encryption (generated if not provided)
            secret_file: Path to encrypted secrets file
        """
        self.secret_file = Path(secret_file) if secret_file else None
        self.secrets: Dict[str, str] = {}
        
        # Initialize encryption
        if master_key:
            self.cipher_suite = Fernet(master_key.encode())
        else:
            # Try to get key from environment
            key = os.environ.get("ASSISTANT_MASTER_KEY")
            if key:
                self.cipher_suite = Fernet(key.encode())
            else:
                # Generate new key
                key = Fernet.generate_key()
                self.cipher_suite = Fernet(key)
                print(f"Generated new master key: {key.decode()}")
                print("Set ASSISTANT_MASTER_KEY environment variable to this value")
        
        # Load existing secrets if file provided
        if self.secret_file and self.secret_file.exists():
            self.load_secrets()
    
    def store_secret(self, key: str, value: str) -> None:
        """Store a secret value.
        
        Args:
            key: Secret key name
            value: Secret value to store
        """
        encrypted_value = self.cipher_suite.encrypt(value.encode())
        self.secrets[key] = encrypted_value.decode()
        
        if self.secret_file:
            self.save_secrets()
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve a secret value.
        
        Args:
            key: Secret key name
            default: Default value if key not found
            
        Returns:
            Decrypted secret value or default
        """
        encrypted_value = self.secrets.get(key)
        if encrypted_value is None:
            return default
        
        try:
            return self.cipher_suite.decrypt(encrypted_value.encode()).decode()
        except Exception:
            # If decryption fails, return default
            return default
    
    def delete_secret(self, key: str) -> bool:
        """Delete a secret.
        
        Args:
            key: Secret key name
            
        Returns:
            True if secret was deleted, False if not found
        """
        if key in self.secrets:
            del self.secrets[key]
            if self.secret_file:
                self.save_secrets()
            return True
        return False
    
    def list_secrets(self) -> List[str]:
        """List all secret keys.
        
        Returns:
            List of secret key names
        """
        return list(self.secrets.keys())
    
    def mask_value(self, value: str, visible_chars: int = 4, mask_char: str = "*") -> str:
        """Mask a value for display purposes.
        
        Args:
            value: Value to mask
            visible_chars: Number of characters to keep visible
            mask_char: Character to use for masking
            
        Returns:
            Masked value
        """
        if len(value) <= visible_chars:
            return mask_char * len(value)
        
        return value[:visible_chars] + mask_char * (len(value) - visible_chars)
    
    def mask_config_dict(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive values in configuration dictionary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configuration with sensitive values masked
        """
        sensitive_patterns = [
            'password', 'secret', 'key', 'token', 'passphrase',
            'api_key', 'private_key', 'auth', 'credential'
        ]
        
        def mask_recursive(obj, path=""):
            if isinstance(obj, dict):
                result = {}
                for k, v in obj.items():
                    current_path = f"{path}.{k}" if path else k
                    if any(pattern in k.lower() for pattern in sensitive_patterns):
                        if isinstance(v, str):
                            result[k] = self.mask_value(v)
                        else:
                            result[k] = "***MASKED***"
                    else:
                        result[k] = mask_recursive(v, current_path)
                return result
            elif isinstance(obj, list):
                return [mask_recursive(item, f"{path}[{i}]") for i, item in enumerate(obj)]
            else:
                return obj
        
        return mask_recursive(config)
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a value.
        
        Args:
            value: Value to encrypt
            
        Returns:
            Encrypted value as base64 string
        """
        encrypted = self.cipher_suite.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a value.
        
        Args:
            encrypted_value: Base64 encrypted value
            
        Returns:
            Decrypted value
        """
        encrypted_bytes = base64.b64decode(encrypted_value.encode())
        decrypted = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def save_secrets(self) -> None:
        """Save encrypted secrets to file."""
        if not self.secret_file:
            raise ValueError("No secret file specified")
        
        self.secret_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.secret_file, 'w') as f:
            json.dump(self.secrets, f)
    
    def load_secrets(self) -> None:
        """Load encrypted secrets from file."""
        if not self.secret_file or not self.secret_file.exists():
            return
        
        with open(self.secret_file, 'r') as f:
            self.secrets = json.load(f)
    
    def rotate_master_key(self, new_master_key: str) -> None:
        """Rotate master key and re-encrypt all secrets.
        
        Args:
            new_master_key: New master key string
        """
        # Decrypt all current secrets
        old_manager = SecretManager(self.cipher_suite.key.decode())
        decrypted_secrets = {}
        
        for key, encrypted_value in self.secrets.items():
            decrypted = old_manager.cipher_suite.decrypt(encrypted_value.encode()).decode()
            decrypted_secrets[key] = decrypted
        
        # Re-encrypt with new key
        self.cipher_suite = Fernet(new_master_key.encode())
        self.secrets.clear()
        
        for key, value in decrypted_secrets.items():
            self.store_secret(key, value)

    @staticmethod
    def generate_master_key() -> str:
        """Generate a new master key.
        
        Returns:
            New master key as string
        """
        return Fernet.generate_key().decode()
    
    @staticmethod
    def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> str:
        """Derive encryption key from password.
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation (generated if not provided)
            
        Returns:
            Master key as string
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.b64encode(kdf.derive(password.encode()))
        return key.decode()


class EnvSecretProvider:
    """Provider for secrets from environment variables."""
    
    def __init__(self, prefix: str = "ASSISTANT_SECRET_"):
        """Initialize environment secret provider.
        
        Args:
            prefix: Prefix for secret environment variables
        """
        self.prefix = prefix
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from environment variable.
        
        Args:
            key: Secret key name
            default: Default value if not found
            
        Returns:
            Secret value or default
        """
        env_var = f"{self.prefix}{key.upper()}"
        return os.environ.get(env_var, default)
    
    def list_secrets(self) -> List[str]:
        """List available secret keys.
        
        Returns:
            List of secret key names
        """
        secrets = []
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                secret_key = key[len(self.prefix):].lower()
                secrets.append(secret_key)
        return secrets


def mask_sensitive_keys(config: Dict[str, Any], visible_chars: int = 4) -> Dict[str, Any]:
    """Mask sensitive keys in configuration dictionary.
    
    Args:
        config: Configuration dictionary
        visible_chars: Number of characters to keep visible
        
    Returns:
        Configuration with sensitive values masked
    """
    manager = SecretManager()  # Initialize just for masking
    return manager.mask_config_dict(config)


def load_secrets_from_sources(
    encrypted_file: Optional[Union[str, Path]] = None,
    use_env_vars: bool = True,
    env_prefix: str = "ASSISTANT_SECRET_"
) -> Dict[str, str]:
    """Load secrets from multiple sources.
    
    Args:
        encrypted_file: Path to encrypted secrets file
        use_env_vars: Whether to use environment variables
        env_prefix: Prefix for environment variable secrets
        
    Returns:
        Dictionary of secrets
    """
    secrets = {}
    
    # Load from encrypted file
    if encrypted_file:
        try:
            manager = SecretManager(secret_file=encrypted_file)
            for key in manager.list_secrets():
                secrets[key] = manager.get_secret(key)
        except Exception:
            pass  # Ignore errors loading from file
    
    # Load from environment variables
    if use_env_vars:
        provider = EnvSecretProvider(env_prefix)
        for key in provider.list_secrets():
            secrets[key] = provider.get_secret(key)
    
    return secrets