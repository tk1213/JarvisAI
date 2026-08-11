from __future__ import annotations

from functools import lru_cache

from pydantic import AliasChoices, Field
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

    app_environment: str = Field(
        default="development",
        validation_alias=AliasChoices(
            "APP_ENVIRONMENT",
            "APP_ENV",
        ),
    )

    debug: bool = False

    wake_word: str = "jarvis"

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------
    log_level: str = "INFO"

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------
    database_url: str = (
        "sqlite+aiosqlite:///./jarvis.db"
    )

    # ---------------------------------------------------------
    # OpenAI
    # ---------------------------------------------------------
    openai_api_key: str | None = Field(
        default=None,
        repr=False,
    )

    openai_model: str = "gpt-5.5"

    openai_timeout_seconds: float = 60.0
    openai_max_retries: int = 2
    openai_max_output_tokens: int | None = None

    # ---------------------------------------------------------
    # Smart Home
    # ---------------------------------------------------------
    smart_home_provider: str = "mock"

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
        validation_alias=AliasChoices(
            "TUYA_ACCESS_KEY",
            "TUYA_ACCESS_SECRET",
        ),
    )

    tuya_device_id: str | None = Field(
        default=None,
        repr=False,
    )

    tuya_endpoint: str = (
        "https://openapi.tuyaus.com"
    )

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
    tts_speed: float = 1.15

    # ---------------------------------------------------------
    # Audio
    # ---------------------------------------------------------
    audio_sample_rate: int = 16000
    audio_channels: int = 1

    @property
    def is_development(self) -> bool:
        return (
            self.app_environment.lower()
            == "development"
        )

    @property
    def is_production(self) -> bool:
        return (
            self.app_environment.lower()
            == "production"
        )

    @property
    def has_openai_credentials(self) -> bool:
        return bool(
            self.openai_api_key
        )

    @property
    def has_tuya_credentials(self) -> bool:
        return bool(
            self.tuya_access_id
            and self.tuya_access_key
        )

    @property
    def use_tuya(self) -> bool:
        return (
            self.smart_home_provider
            .lower()
            .strip()
            == "tuya"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()