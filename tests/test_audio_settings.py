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

def test_audio_device_identity_settings_load_from_environment(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "AUDIO_INPUT_DEVICE_NAME",
        "Desktop Microphone (RØDE NT-USB Mini)",
    )
    monkeypatch.setenv(
        "AUDIO_INPUT_DEVICE_HOST_API",
        "Windows DirectSound",
    )
    monkeypatch.setenv(
        "AUDIO_OUTPUT_DEVICE_NAME",
        "Speakers (Realtek(R) Audio)",
    )
    monkeypatch.setenv(
        "AUDIO_OUTPUT_DEVICE_HOST_API",
        "Windows WASAPI",
    )

    settings = Settings(
        _env_file=None,
    )

    assert settings.audio_input_device_name == (
        "Desktop Microphone (RØDE NT-USB Mini)"
    )
    assert settings.audio_input_device_host_api == (
        "Windows DirectSound"
    )
    assert settings.audio_output_device_name == (
        "Speakers (Realtek(R) Audio)"
    )
    assert settings.audio_output_device_host_api == (
        "Windows WASAPI"
    )


def test_audio_device_identity_settings_default_to_none() -> None:
    settings = Settings(
        _env_file=None,
    )

    assert settings.audio_input_device_name is None
    assert settings.audio_input_device_host_api is None
    assert settings.audio_output_device_name is None
    assert settings.audio_output_device_host_api is None