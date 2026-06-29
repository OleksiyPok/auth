# app/core/config.py

from enum import Enum


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


class Settings(BaseSettings):
    # Environment
    ENV: EnvironmentEnum = EnvironmentEnum.PROD

    # Services setting
    LOGIN_FIELD: LoginFieldEnum = LoginFieldEnum.EMAIL  # Login primary UI key
    EMAIL_SERVICE: EmailServiceEnum = EmailServiceEnum.MAILTRAP

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
