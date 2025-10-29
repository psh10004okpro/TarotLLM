"""
Application Configuration
Environment variables and settings management
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Unwoldam Tarot API"
    VERSION: str = "1.0.0"

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["*"]

    # LLM Provider API Keys
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    # LLM Model Settings
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # Default LLM Provider
    DEFAULT_LLM_PROVIDER: str = "claude"

    # RAG Settings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    VECTOR_STORE_PATH: str = "./data/vector_store"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # Session Settings
    SESSION_EXPIRY_HOURS: int = 24
    MAX_SESSION_HISTORY: int = 100

    # TTS/STT Settings (for future implementation)
    TTS_PROVIDER: Optional[str] = None
    STT_PROVIDER: Optional[str] = None

    # Database Settings (for future implementation)
    DATABASE_URL: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
