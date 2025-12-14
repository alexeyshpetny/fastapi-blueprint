from pydantic_settings import SettingsConfigDict

from src.core.settings.app import AppSettings
from src.core.settings.db import DatabaseSettings


class Settings(AppSettings, DatabaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        env_prefix="APP_",
    )


settings = Settings()
