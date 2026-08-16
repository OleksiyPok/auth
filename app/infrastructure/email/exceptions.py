# app/infrastructure/email/exceptions.py

from fastapi import status

from app.core.exceptions import AppError


class EmailInfrastructureError(AppError):
    """
    Base exception for Email service errors.
    """


class ProviderRegisterError(EmailInfrastructureError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "PROVIDER_REGISTER_ERROR"
    message = "Email provider not registered"


class ProviderConfigurationError(EmailInfrastructureError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "PROVIDER_CONFIGURATION_ERROR"
    message = "Mailjet credentials are not configured"


class ExternalServiceError(EmailInfrastructureError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "PROVIDER_CONFIGURATION_ERROR"
    message = "Provider configuration error"
