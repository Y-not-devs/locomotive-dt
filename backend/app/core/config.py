from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    app_title: str = "Locomotive Digital Twin API"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/locomotive_dt"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    simulator_enabled: bool = True
    simulator_interval_ms: int = 1000
    simulator_locomotive_id: str = "KZ-LOC-001"
    history_buffer_size: int = 900
    health_index_config_path: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[1] / "config" / "health_index.json"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, str):
            if value.startswith("["):
                return [item.strip().strip('"') for item in value.strip("[]").split(",") if item.strip()]
            return [value]
        return value


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
