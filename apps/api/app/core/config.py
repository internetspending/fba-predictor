"""Application configuration using Pydantic settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database configuration
    database_url: str = Field(
        default="postgresql+psycopg://fba_user:fba_pass@localhost:5432/fba_predictor",
        description="Database connection URL",
    )

    # Redis configuration
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")

    # CORS configuration
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        description="Comma-separated list of allowed CORS origins",
    )

    # Application settings
    app_env: str = Field(default="development", description="Application environment")
    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # External API Keys
    keepa_api_key: str = Field(default="your_keepa_api_key_here", description="Keepa API key")

    # API Configuration
    api_title: str = Field(default="FBA Profit Predictor", description="API title")
    api_version: str = Field(default="0.1.0", description="API version")

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
