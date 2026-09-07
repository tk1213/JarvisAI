from __future__ import annotations

from jarvis.config.settings import Settings


def test_audio_device_settings_load_from_environment(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "AUDIO_INPUT_DEVICE",
        "12",
    )
    monkeypatch.setenv(
        "AUDIO_OUTPUT_DEVICE",
        "9",
    )

    settings = Settings(
        _env_file=None,
    )

    assert settings.audio_input_device == 12
    assert settings.audio_output_device == 9


def test_audio_device_settings_default_to_automatic() -> None:
    settings = Settings(
        _env_file=None,
    )

    assert settings.audio_input_device is None
    assert settings.audio_output_device is None