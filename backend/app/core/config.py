from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Read .env, be case-sensitive, and IGNORE extra env keys we don't model explicitly
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "CPS Platform"

    # Auth / JWT
    SECRET_KEY: str = "change-this-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # --- Database ---
    # Support BOTH names. Prefer SQLALCHEMY_DATABASE_URI if set, else DATABASE_URL.
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    DATABASE_URL: Optional[str] = Field(default=None)

    # --- Optional extras you already have in your .env ---
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = 6379
    CAPTCHA_ENCRYPTION_KEY: Optional[str] = None

    @property
    def DB_URL(self) -> str:
        return (
            self.SQLALCHEMY_DATABASE_URI
            or self.DATABASE_URL
            or "sqlite:///./dev.db"
        )


settings = Settings()
