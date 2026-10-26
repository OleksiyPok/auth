# app/infrastructure/encryption.py

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


class EncryptionKeyNotConfiguredError(Exception):
    """SECRETS_ENCRYPTION_KEY is not set."""


class SecretDecryptionError(Exception):
    """The value is damaged or was encrypted with another key."""


def _fernet(key: str | None) -> Fernet:
    key = key or settings.SECRETS_ENCRYPTION_KEY
    if not key:
        raise EncryptionKeyNotConfiguredError()
    return Fernet(key.encode())


def encrypt_secret(value: str, key: str | None = None) -> str:
    """Encrypt a secret for storage. The key defaults to the one in settings."""
    return _fernet(key).encrypt(value.encode()).decode()


def decrypt_secret(token: str, key: str | None = None) -> str:
    """Decrypt a stored secret. Fails with SecretDecryptionError on a wrong key."""
    try:
        return _fernet(key).decrypt(token.encode()).decode()
    except InvalidToken as exc:
        raise SecretDecryptionError() from exc
