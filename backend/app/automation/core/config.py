# backend/app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CPS Automation API"
    SECRET_KEY: str = "dev-secret"
    # Simple demo token; change for production or wire real JWT
    ACCESS_TOKEN: str = "demo"
    # Uses local SQLite DB by default (folder auto-created)
    DATABASE_URL: str = "sqlite:///data/app.db"

    class Config:
        env_file = ".env"

settings = Settings()
