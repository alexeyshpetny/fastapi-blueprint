from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DOC_TITLE: str = Field(default="FastAPI Template")
    DOC_VERSION: str = Field(default="1.0.0")
    DOC_DESCRIPTION: str = Field(default="API documentation for FastAPI template")
    DOC_OPENAPI_URL: str = Field(default="/api/openapi.json")
    DOC_OPENAPI_VERSION: str = Field(default="3.0.2")
    DOC_SWAGGER_URL: str = Field(default="/api/docs")
    DOC_REDOC_URL: str = Field(default="/api/redoc")

    CORS_ALLOW_ORIGINS: list[str] = Field(default=["*"])
    CORS_ALLOW_METHODS: list[str] = Field(default=["*"])
    CORS_ALLOW_HEADERS: list[str] = Field(default=["*"])
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_MAX_AGE: int = Field(default=600, ge=0)

    TESTING: bool = Field(default=False)

    API_V1_PREFIX: str = Field(default="/api/v1")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        env_prefix="APP_",
    )


settings = Settings()
