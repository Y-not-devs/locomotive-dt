from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    cors_allow_origins: list[str] = ["*"]
    db_path: str = "data/telemetry.db"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
