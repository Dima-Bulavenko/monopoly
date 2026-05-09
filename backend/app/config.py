"""Application configuration via pydantic-settings."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "local"
    dynamodb_table_name: str = "monopoly"
    aws_region: str = "us-east-1"
    dynamodb_endpoint_url: str | None = None
    apigw_management_endpoint: str | None = None

    # Auth
    database_url: str = "postgresql+asyncpg://localhost/monopoly"
    jwt_private_key_pem: str = ""
    jwt_public_key_pem: str = ""
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    google_client_id: str | None = None
    apple_client_id: str | None = None

    @property
    def is_local(self) -> bool:
        return self.env == "local"


settings = Settings()
