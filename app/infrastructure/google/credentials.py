# app/infrastructure/google/credentials.py

from datetime import timezone

from cryptography.fernet import Fernet
from google.oauth2.credentials import Credentials

from app.core.config import settings
from app.infrastructure.google.config import GOOGLE_OAUTH_SCOPES
from app.infrastructure.google.exceptions import GoogleCredentialsError


def _get_fernet() -> Fernet:
    return Fernet(settings.GOOGLE_TOKEN_ENCRYPTION_KEY.encode())


def encrypt_token(token: str) -> str:
    try:
        return (
            _get_fernet()
            .encrypt(
                token.encode(),
            )
            .decode()
        )
    except Exception as exc:
        raise GoogleCredentialsError() from exc


def decrypt_token(token: str) -> str:
    try:
        return (
            _get_fernet()
            .decrypt(
                token.encode(),
            )
            .decode()
        )
    except Exception as exc:
        raise GoogleCredentialsError() from exc


def credentials_to_dict(credentials: Credentials) -> dict:
    if not credentials.token:
        raise GoogleCredentialsError()

    if not credentials.refresh_token:
        raise GoogleCredentialsError()

    expiry = credentials.expiry

    if expiry is not None and expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    return {
        "access_token": encrypt_token(credentials.token),
        "refresh_token": encrypt_token(credentials.refresh_token),
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": list(credentials.scopes or GOOGLE_OAUTH_SCOPES),
        "expiry": expiry,
    }


def credentials_from_account(account) -> Credentials:
    return Credentials(
        token=decrypt_token(account.access_token),
        refresh_token=decrypt_token(account.refresh_token),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=GOOGLE_OAUTH_SCOPES,
    )
