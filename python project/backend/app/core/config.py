from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="PG Management System")
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)
    secret_key: str = Field(default="change-me-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60)

    postgres_db: str = Field(default="pg_management")
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    database_url: str = Field(default="postgresql+psycopg://postgres:postgres@localhost:5432/pg_management")

    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def sqlalchemy_database_url(self) -> str:
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
