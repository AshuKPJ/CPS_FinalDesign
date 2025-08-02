# backend/app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import PostgresDsn

class Settings(BaseSettings):
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: PostgresDsn

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # CAPTCHA Encryption
    CAPTCHA_ENCRYPTION_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
