"""
Configuration management for AI Parliament application.
Uses pydantic-settings for environment variable management.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 500

    # Database Configuration
    database_url: str = "sqlite:///./ai_parliament.db"

    # Redis Configuration (for caching)
    redis_url: Optional[str] = None
    redis_enabled: bool = False
    cache_ttl: int = 3600  # 1 hour default

    # Server Configuration
    debug: bool = False
    cors_origins: list = ["http://localhost:3000", "http://localhost:3001"]

    # API Configuration
    rate_limit_per_minute: int = 10
    max_debate_responses: int = 10

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/parliament.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures we only load settings once.
    """
    return Settings()


# Export settings instance
settings = get_settings()
