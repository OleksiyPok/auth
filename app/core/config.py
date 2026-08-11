# app/core/config.py

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

    CORS_ORIGINS: list[str] = []

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    SUPERADMIN_LOGIN: str
    SUPERADMIN_PASSWORD: str
    SUPERADMIN_EMAIL: str
    SUPERADMIN_FIRST_NAME: str = "System"
    SUPERADMIN_LAST_NAME: str = "Superadministrator"


settings = Settings()
