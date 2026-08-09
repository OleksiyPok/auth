# app/infrastructure/google/exceptions.py


class GoogleInfrastructureError(Exception):
    """Base exception for Google infrastructure errors."""


class GoogleOAuthError(GoogleInfrastructureError):
    """Google OAuth authorization failed."""


class GoogleCredentialsError(GoogleInfrastructureError):
    """Google credentials operation failed."""


class GoogleAPIRequestError(GoogleInfrastructureError):
    """Google API request failed."""
