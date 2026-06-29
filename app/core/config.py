# app/core/config.py

from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.users.model import User


class EnvironmentEnum(str, Enum):
    DEV = "DEV"
    PROD = "PROD"


# Login primary UI key
class LoginFieldEnum(str, Enum):
    EMAIL = "email"
    USERNAME = "username"


class EmailServiceEnum(str, Enum):
    MAILTRAP = "mailtrap"
    MAILJET = "mailjet"
    RESEND = "resend"
    SENDPULSE = "sendpulse"
    MAILERLITE = "mailerlite"


class Settings(BaseSettings):
    # Environment
    ENV: EnvironmentEnum = EnvironmentEnum.PROD

    # Services setting
    LOGIN_FIELD: LoginFieldEnum = LoginFieldEnum.EMAIL  # Login primary UI key
    EMAIL_SERVICE: EmailServiceEnum = EmailServiceEnum.RESEND

    # Auth / JWT
    SECRET_KEY: str = "abracadabra"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MAIL_FROM_EMAIL: str | None = "noreply@example.com"
    MAIL_FROM_NAME: str | None = "My App"

    # Email (Mailtrap)
    MAILTRAP_USER: str | None
    MAILTRAP_SMTP_PASSWORD: str | None
    MAILTRAP_SMTP_HOST: str | None = "smtp.mailtrap.io"
    MAILTRAP_SMTP_PORT: int | None = 587

    # Email (Mailjet)
    MAILJET_API_KEY: str | None
    MAILJET_SECRET_KEY: str | None

    # Email (Resend)
    RESEND_API_KEY: str | None

    # Email (Mailerlite)
    MAILERLITE_API_KEY: str | None

    # Email (SendPulse)
    SENDPULSE_API_USER: str | None
    SENDPULSE_SECRET_KEY: str | None

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    def validate_login_field(self) -> None:
        if self.LOGIN_FIELD.value not in User.model_fields:
            raise ValueError(
                f"Invalid LOGIN_FIELD '{self.LOGIN_FIELD.value}'. "
                "User model has no such field."
            )

    def validate_email_service(self) -> None:

        if self.EMAIL_SERVICE == EmailServiceEnum.MAILTRAP:
            if not self.MAILTRAP_USER or not self.MAILTRAP_SMTP_PASSWORD:
                raise ValueError("Mailtrap credentials are not configured")

        if self.EMAIL_SERVICE == EmailServiceEnum.MAILJET:
            if not self.MAILJET_API_KEY or not self.MAILJET_SECRET_KEY:
                raise ValueError("Mailjet credentials are not configured")

        if self.EMAIL_SERVICE == EmailServiceEnum.RESEND:
            if not self.RESEND_API_KEY:
                raise ValueError("Resend credentials are not configured")

        if self.EMAIL_SERVICE == EmailServiceEnum.MAILERLITE:
            if not self.MAILERLITE_API_KEY:
                raise ValueError("Mailerlite API key is not configured")

        if self.EMAIL_SERVICE == EmailServiceEnum.SENDPULSE:
            if not self.SENDPULSE_API_USER or not self.SENDPULSE_SECRET_KEY:
                raise ValueError("SendPulse credentials are not configured")

    @property
    def is_dev(self) -> bool:
        return self.ENV == EnvironmentEnum.DEV

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
settings.validate_login_field()
settings.validate_email_service()
