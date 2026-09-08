from __future__ import annotations

import pytest

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

def test_set_input_device_persists_identity(
    tmp_path,
) -> None:
    env_file = tmp_path / ".env"
    config = AudioDeviceConfig(
        env_file=env_file,
    )

    config.set_input_device(
        8,
        name="Desktop Microphone (RØDE NT-USB Mini)",
        host_api="Windows DirectSound",
    )

    content = env_file.read_text(
        encoding="utf-8",
    )

    assert "AUDIO_INPUT_DEVICE=8" in content
    assert (
        "AUDIO_INPUT_DEVICE_NAME="
        "Desktop Microphone (RØDE NT-USB Mini)"
        in content
    )
    assert (
        "AUDIO_INPUT_DEVICE_HOST_API="
        "Windows DirectSound"
        in content
    )


def test_set_output_device_persists_identity(
    tmp_path,
) -> None:
    env_file = tmp_path / ".env"
    config = AudioDeviceConfig(
        env_file=env_file,
    )

    config.set_output_device(
        16,
        name="Speakers (Realtek(R) Audio)",
        host_api="Windows WASAPI",
    )

    content = env_file.read_text(
        encoding="utf-8",
    )

    assert "AUDIO_OUTPUT_DEVICE=16" in content
    assert (
        "AUDIO_OUTPUT_DEVICE_NAME="
        "Speakers (Realtek(R) Audio)"
        in content
    )
    assert (
        "AUDIO_OUTPUT_DEVICE_HOST_API="
        "Windows WASAPI"
        in content
    )

def test_reset_input_device_removes_identity(
    tmp_path,
) -> None:
    env_file = tmp_path / ".env"
    config = AudioDeviceConfig(
        env_file=env_file,
    )

    config.set_input_device(
        8,
        name="USB Microphone",
        host_api="Windows DirectSound",
    )

    config.reset_input_device()

    content = env_file.read_text(
        encoding="utf-8",
    )

    assert "AUDIO_INPUT_DEVICE=" not in content
    assert "AUDIO_INPUT_DEVICE_NAME=" not in content
    assert "AUDIO_INPUT_DEVICE_HOST_API=" not in content


def test_reset_output_device_removes_identity(
    tmp_path,
) -> None:
    env_file = tmp_path / ".env"
    config = AudioDeviceConfig(
        env_file=env_file,
    )

    config.set_output_device(
        16,
        name="Speakers",
        host_api="Windows WASAPI",
    )

    config.reset_output_device()

    content = env_file.read_text(
        encoding="utf-8",
    )

    assert "AUDIO_OUTPUT_DEVICE=" not in content
    assert "AUDIO_OUTPUT_DEVICE_NAME=" not in content
    assert "AUDIO_OUTPUT_DEVICE_HOST_API=" not in content

def test_set_input_device_rejects_incomplete_identity_without_writing(
    tmp_path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("EXISTING=value\n", encoding="utf-8")
    config = AudioDeviceConfig(env_file=env_file)

    with pytest.raises(
        ValueError,
        match="Audio device identity requires both name and host API",
    ):
        config.set_input_device(
            8,
            name="USB Microphone",
        )

    assert env_file.read_text(encoding="utf-8") == "EXISTING=value\n"


def test_set_output_device_rejects_incomplete_identity_without_writing(
    tmp_path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("EXISTING=value\n", encoding="utf-8")
    config = AudioDeviceConfig(env_file=env_file)

    with pytest.raises(
        ValueError,
        match="Audio device identity requires both name and host API",
    ):
        config.set_output_device(
            9,
            host_api="Windows WASAPI",
        )

    assert env_file.read_text(encoding="utf-8") == "EXISTING=value\n"