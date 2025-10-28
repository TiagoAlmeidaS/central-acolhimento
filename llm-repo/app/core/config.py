"""LLM Service configuration."""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """LLM Service settings."""

    # Application
    PROJECT_NAME: str = "Central de Acolhimento LLM Service"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Ollama Configuration
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b"
    OLLAMA_TIMEOUT: int = 60
    OLLAMA_MAX_RETRIES: int = 3

    # MCP Configuration
    MCP_PORT: int = 8002
    MCP_HOST: str = "0.0.0.0"

    # Entity Extraction
    EXTRACTION_TIMEOUT: int = 30
    MAX_TEXT_LENGTH: int = 2000
    MIN_CONFIDENCE: float = 0.7

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Prompt Templates
    PROMPT_TEMPLATE_PATH: str = "app/prompt_templates/"
    DEFAULT_TEMPLATE: str = "entity_extraction.jinja2"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
