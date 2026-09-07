from __future__ import annotations

from jarvis.config.audio_device_config import (
    AudioDeviceConfig,
)


def test_set_input_device_preserves_other_env_values(
    tmp_path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "OPENAI_API_KEY=secret-value\n"
        "APP_ENVIRONMENT=development\n",
        encoding="utf-8",
    )

    config = AudioDeviceConfig(
        env_file=env_file,
    )

    config.set_input_device(12)

    content = env_file.read_text(
        encoding="utf-8",
    )

    assert "AUDIO_INPUT_DEVICE=12" in content
    assert "OPENAI_API_KEY=secret-value" in content
    assert "APP_ENVIRONMENT=development" in content


def test_set_output_device_updates_existing_value(
    tmp_path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "AUDIO_OUTPUT_DEVICE=4\n",
        encoding="utf-8",
    )

    config = AudioDeviceConfig(
        env_file=env_file,
    )

    config.set_output_device(9)

    content = env_file.read_text(
        encoding="utf-8",
    )

    assert "AUDIO_OUTPUT_DEVICE=9" in content
    assert "AUDIO_OUTPUT_DEVICE=4" not in content
    assert content.count(
        "AUDIO_OUTPUT_DEVICE="
    ) == 1


def test_reset_input_device_removes_persisted_value(
    tmp_path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "OPENAI_API_KEY=secret-value\n"
        "AUDIO_INPUT_DEVICE=12\n",
        encoding="utf-8",
    )

    config = AudioDeviceConfig(
        env_file=env_file,
    )

    config.reset_input_device()

    content = env_file.read_text(
        encoding="utf-8",
    )

    assert "AUDIO_INPUT_DEVICE=" not in content
    assert "OPENAI_API_KEY=secret-value" in content


def test_reset_output_device_removes_persisted_value(
    tmp_path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "AUDIO_OUTPUT_DEVICE=9\n"
        "APP_ENVIRONMENT=development\n",
        encoding="utf-8",
    )

    config = AudioDeviceConfig(
        env_file=env_file,
    )

    config.reset_output_device()

    content = env_file.read_text(
        encoding="utf-8",
    )

    assert "AUDIO_OUTPUT_DEVICE=" not in content
    assert "APP_ENVIRONMENT=development" in content