"""
Encryption utilities for sensitive data like API keys and secrets.

Uses Fernet (symmetric encryption) for encrypting/decrypting sensitive data at rest.
The encryption key is derived from the application's secret key.
"""

import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import settings


def _get_encryption_key() -> bytes:
    """
    Derive an encryption key from the application secret key.

    Uses PBKDF2 to derive a Fernet-compatible key from the secret.
    """
    # Use a fixed salt for key derivation (we could make this configurable)
    salt = b"scims_integration_encryption_salt_v1"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.secret_key.encode()))
    return key


_fernet = None


def _get_fernet() -> Fernet:
    """Get or create the Fernet encryption instance."""
    global _fernet
    if _fernet is None:
        key = _get_encryption_key()
        _fernet = Fernet(key)
    return _fernet


def encrypt_value(value: str) -> str:
    """
    Encrypt a plain text value (e.g., API key, secret).

    Args:
        value: Plain text string to encrypt

    Returns:
        Encrypted string (base64-encoded)
    """
    if not value:
        return ""
    fernet = _get_fernet()
    encrypted = fernet.encrypt(value.encode())
    return encrypted.decode()


def decrypt_value(encrypted_value: str) -> Optional[str]:
    """
    Decrypt an encrypted value.

    Args:
        encrypted_value: Encrypted string (base64-encoded)

    Returns:
        Decrypted plain text string, or None if decryption fails
    """
    if not encrypted_value:
        return None
    try:
        fernet = _get_fernet()
        decrypted = fernet.decrypt(encrypted_value.encode())
        return decrypted.decode()
    except Exception:
        # Decryption failed (invalid key, corrupted data, etc.)
        return None
