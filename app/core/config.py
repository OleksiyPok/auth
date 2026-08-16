# app/core/config.py

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core import static_config


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    DEBUG: bool = False

    APP_NAME: str = static_config.APP_NAME
    APP_VERSION: str = static_config.APP_VERSION

    API_V1_PREFIX: str = static_config.API_V1_PREFIX
    API_V2_PREFIX: str = static_config.API_V2_PREFIX

    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    CORS_ORIGINS: list[str] = Field(default_factory=list)

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Email
    EMAIL_SERVICE: str = "dummy"

    # Sender
    MAIL_FROM_EMAIL: str | None = None
    MAIL_FROM_NAME: str | None = None

    # Mailtrap
    MAILTRAP_USER: str | None = None
    MAILTRAP_SMTP_PASSWORD: str | None = None

    MAILTRAP_SMTP_HOST: str | None = None
    MAILTRAP_SMTP_PORT: int = 587
    MAILTRAP_USE_TLS: bool = True

    # Mailjet
    MAILJET_API_KEY: str | None = None
    MAILJET_SECRET_KEY: str | None = None

    # Seed data
    SUPERADMIN_LOGIN: str
    SUPERADMIN_PASSWORD: str
    SUPERADMIN_EMAIL: str
    SUPERADMIN_FIRST_NAME: str = "System"
    SUPERADMIN_LAST_NAME: str = "Superadministrator"

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str


settings = Settings()
