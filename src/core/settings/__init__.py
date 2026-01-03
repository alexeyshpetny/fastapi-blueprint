from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.settings.app import AppSettings
from src.core.settings.auth import AuthSettings
from src.core.settings.cache import CacheSettings
from src.core.settings.db import DatabaseSettings
from src.core.settings.logging import LoggingSettings


class Settings(
    AppSettings,
    DatabaseSettings,
    LoggingSettings,
    CacheSettings,
    AuthSettings,
):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        env_prefix="APP_",
    )

    def model_post_init(self, _) -> None:
        """Automatically call all parent model_post_init methods."""
        for cls in self.__class__.__mro__[1:]:
            if cls is object:
                continue
            if (
                hasattr(cls, "model_post_init")
                and cls.model_post_init is not BaseSettings.model_post_init
                and cls.model_post_init is not object.__init__
            ):
                cls.model_post_init(self, _)


settings = Settings()
