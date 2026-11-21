from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Corporate Event Management API"
    app_version: str = "1.0.0"
    app_env: str = "development"
    database_url: str = "sqlite:///./corporate_events.db"
    jwt_secret: str = "local-development-secret-change-before-deploy-123456"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = Field(default=30, ge=5, le=1440)
    cors_origins: str = "http://localhost:8000,http://127.0.0.1:8000"
    allowed_hosts: str = "*"
    auto_create_tables: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def allowed_host_list(self) -> list[str]:
        return [item.strip() for item in self.allowed_hosts.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.app_env.lower() == "production":
        if settings.jwt_secret.startswith("local-development-secret"):
            raise RuntimeError("JWT_SECRET must be replaced before production deployment.")
        if len(settings.jwt_secret) < 32:
            raise RuntimeError("JWT_SECRET must contain at least 32 characters.")
        if settings.database_url.startswith("sqlite"):
            raise RuntimeError("A persistent PostgreSQL DATABASE_URL is required in production.")
        if settings.auto_create_tables:
            raise RuntimeError("AUTO_CREATE_TABLES must be false in production; apply migrations explicitly.")
    return settings
