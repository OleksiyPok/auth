# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core import static_config


class Settings(BaseSettings):

    APP_NAME: str = static_config.APP_NAME
    APP_VERSION: str = static_config.APP_VERSION

    API_V1_PREFIX: str = static_config.API_V1_PREFIX
    API_V2_PREFIX: str = static_config.API_V2_PREFIX

    DATABASE_URL: str = "sqlite:///./app.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
