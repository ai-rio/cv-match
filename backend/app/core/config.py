from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    ENVIRONMENT: str = "development"

    # CORS
    CORS_ORIGINS: list[str] | str = ["http://localhost:3000"]

    # Supabase
    SUPABASE_URL: str = "http://localhost:54321"
    SUPABASE_SERVICE_KEY: str = "your_service_key_here"

    # LLM
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Vector Database
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "default_collection"

    # Security Settings
    # Input Sanitization
    MAX_PROMPT_LENGTH: int = 10000
    MAX_TEXT_LENGTH: int = 50000
    MAX_QUERY_LENGTH: int = 1000
    ALLOW_HTML_TAGS: bool = False
    ALLOW_MARKDOWN: bool = True
    ALLOW_URLS: bool = True
    BLOCK_SYSTEM_PROMPTS: bool = True
    BLOCK_ROLE_INSTRUCTIONS: bool = True
    BLOCK_JSON_INSTRUCTIONS: bool = True
    BLOCK_CODE_EXECUTION: bool = True

    # Rate Limiting
    RATE_LIMIT_PER_USER: int = 60  # requests per minute
    RATE_LIMIT_PER_IP: int = 100   # requests per minute
    ENABLE_RATE_LIMITING: bool = True

    # Security Monitoring
    ENABLE_SECURITY_LOGGING: bool = True
    LOG_SECURITY_EVENTS: bool = True
    SECURITY_LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Initialize settings
settings = Settings()

# Parse CORS origins from comma-separated string if provided that way
if isinstance(settings.CORS_ORIGINS, str):
    # Handle potential issues with quotes and spacing
    origins_str = settings.CORS_ORIGINS.strip()
    if origins_str.startswith('"') and origins_str.endswith('"'):
        origins_str = origins_str[1:-1]
    elif origins_str.startswith("'") and origins_str.endswith("'"):
        origins_str = origins_str[1:-1]

    settings.CORS_ORIGINS = [origin.strip() for origin in origins_str.split(",")]