from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    pghost: str = Field(min_length=1)
    pgdatabase: str = Field(min_length=1)
    pguser: str = Field(min_length=1)
    pgpassword: str = Field(min_length=1)
    pgport: int = Field(default=5432, ge=1, le=65535)
    pgsslmode: str = "require"
    jwt_secret_key: str = Field(min_length=32)
    jwt_access_token_minutes: int = Field(default=480, ge=5, le=1440)
    cors_origins: str = "http://localhost:4200"
    app_timezone: str = "America/Lima"

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip().rstrip("/") for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

