# app/two_factor/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    CHALLENGE_EXPIRE_MINUTES: int = 10
    MAX_ATTEMPTS: int = 5
    CODE_LENGTH: int = 6
    RESEND_COOLDOWN_SECONDS: int = 60

settings = Settings()
