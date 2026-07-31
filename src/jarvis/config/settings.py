from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------
    app_name: str = "JarvisAI"
    app_environment: str = "development"
    debug: bool = False

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------
    log_level: str = "INFO"

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------
    database_url: str = "sqlite+aiosqlite:///./jarvis.db"

    # ---------------------------------------------------------
    # OpenAI
    # ---------------------------------------------------------
    openai_api_key: str | None = Field(
        default=None,
        repr=False,
    )
    openai_model: str = "gpt-5.5"

    # ---------------------------------------------------------
    # Tuya
    # ---------------------------------------------------------
    tuya_access_id: str | None = Field(
        default=None,
        repr=False,
    )
    tuya_access_key: str | None = Field(
        default=None,
        repr=False,
    )
    tuya_endpoint: str = "https://openapi.tuyaus.com"

    # ---------------------------------------------------------
    # Speech-to-text
    # ---------------------------------------------------------
    stt_model: str = "base"
    stt_language: str = "th"

    # ---------------------------------------------------------
    # Text-to-speech
    # ---------------------------------------------------------
    tts_model: str = "gpt-4o-mini-tts"
    tts_language: str = "th"

    # ---------------------------------------------------------
    # Audio
    # ---------------------------------------------------------
    audio_sample_rate: int = 16000
    audio_channels: int = 1

    @property
    def is_development(self) -> bool:
        return self.app_environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        return self.app_environment.lower() == "production"

    @property
    def has_openai_credentials(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def has_tuya_credentials(self) -> bool:
        return bool(
            self.tuya_access_id
            and self.tuya_access_key
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()