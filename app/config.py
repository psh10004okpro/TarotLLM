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
    CLAUDE_MODEL: str = "claude-sonnet-4-5-20250929"
    OPENAI_MODEL: str = "gpt-4-turbo"
    GEMINI_MODEL: str = "gemini-pro"

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

    # Prompt System Settings
    USE_OPTIMIZED_PROMPTS: bool = True           # Enable 2-stage prompt system
    USE_DETAILED_ON_FIRST: bool = True           # Use detailed prompt on first message
    USE_DETAILED_ON_COMPLEX: bool = True         # Use detailed prompt for complex questions
    PROMPT_TOKEN_BUDGET: int = 4000              # Maximum tokens for system prompt
    AUTO_ASSESS_COMPLEXITY: bool = True          # Automatically assess question complexity

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


# Tarot Master Configuration
TAROT_MASTERS = {
    "master_1": {
        "id": 1,
        "name": "달빛의 현자",
        "name_en": "Sage of Moonlight",
        "llm_provider": "claude",
        "model": "claude-sonnet-4-5-20250929",
        "interpret_reversed": True,
        "description": "깊이 있는 심리학적 해석",
        "style": "philosophical, psychological, profound"
    },
    "master_2": {
        "id": 2,
        "name": "별빛의 안내자",
        "name_en": "Starlight Guide",
        "llm_provider": "openai",
        "model": "gpt-4-turbo",
        "interpret_reversed": False,  # 정방향만
        "description": "따뜻한 격려와 희망",
        "style": "warm, empathetic, encouraging, practical"
    },
    "master_3": {
        "id": 3,
        "name": "운명의 해석자",
        "name_en": "Destiny Interpreter",
        "llm_provider": "gemini",
        "model": "gemini-pro",
        "interpret_reversed": True,  # 설정 가능
        "description": "신비로운 스토리텔링",
        "style": "intuitive, mystical, poetic, storytelling"
    }
}
