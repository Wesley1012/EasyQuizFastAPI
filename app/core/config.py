from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # База данных
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    # Настройки приложения
    APP_NAME: str = "Quiz Learning Platform"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-here"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()