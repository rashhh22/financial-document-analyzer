import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8000
    OPENAI_API_KEY: str | None = None
    MODEL_NAME: str = "gpt-4o-mini"
    ANALYZER_PROVIDER: str = "crewai"
    REDIS_URL: str = "redis://localhost:6379/0"
    DATABASE_URL: str = "sqlite:///./app.db"
    class Config: env_file = ".env"
settings = Settings()
