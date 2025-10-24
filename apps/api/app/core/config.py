"""Application configuration using Pydantic settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

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

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
