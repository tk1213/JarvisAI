from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from jarvis.cli import (
    reset_audio_devices,
    set_audio_input_device,
    set_audio_output_device,
)


def test_set_audio_input_device_validates_before_persisting() -> None:
    selected = Mock()
    selected.index = 12
    selected.name = "Desktop Microphone"
    selected.host_api = "Windows DirectSound"

    audio = Mock()
    audio.select_input.return_value = selected

    config = Mock()

    with (
        patch(
            "jarvis.cli.AudioManager",
            return_value=audio,
        ),
        patch(
            "jarvis.cli.AudioDeviceConfig",
            return_value=config,
        ),
    ):
        set_audio_input_device(12)

    audio.select_input.assert_called_once_with(12)
    config.set_input_device.assert_called_once_with(
        12,
        name="Desktop Microphone",
        host_api="Windows DirectSound",
    )


def test_invalid_audio_input_device_is_not_persisted() -> None:
    audio = Mock()
    audio.select_input.side_effect = ValueError(
        "Audio device 999 was not found."
    )

    config = Mock()

    with (
        patch(
            "jarvis.cli.AudioManager",
            return_value=audio,
        ),
        patch(
            "jarvis.cli.AudioDeviceConfig",
            return_value=config,
        ),
        pytest.raises(
            ValueError,
            match="Audio device 999 was not found",
        ),
    ):
        set_audio_input_device(999)

    config.set_input_device.assert_not_called()


def test_set_audio_output_device_validates_before_persisting() -> None:
    selected = Mock()
    selected.index = 9
    selected.name = "Speakers"
    selected.host_api = "Windows WASAPI"

    audio = Mock()
    audio.select_output.return_value = selected

    config = Mock()

    with (
        patch(
            "jarvis.cli.AudioManager",
            return_value=audio,
        ),
        patch(
            "jarvis.cli.AudioDeviceConfig",
            return_value=config,
        ),
    ):
        set_audio_output_device(9)

    audio.select_output.assert_called_once_with(9)
    config.set_output_device.assert_called_once_with(
        9,
        name="Speakers",
        host_api="Windows WASAPI",
    )


def test_invalid_audio_output_device_is_not_persisted() -> None:
    audio = Mock()
    audio.select_output.side_effect = ValueError(
        "Audio device 999 was not found."
    )

    config = Mock()

    with (
        patch(
            "jarvis.cli.AudioManager",
            return_value=audio,
        ),
        patch(
            "jarvis.cli.AudioDeviceConfig",
            return_value=config,
        ),
        pytest.raises(
            ValueError,
            match="Audio device 999 was not found",
        ),
    ):
        set_audio_output_device(999)

    config.set_output_device.assert_not_called()


def test_reset_audio_devices_removes_both_persisted_devices() -> None:
    config = Mock()

    with patch(
        "jarvis.cli.AudioDeviceConfig",
        return_value=config,
    ):
        reset_audio_devices()

    config.reset_input_device.assert_called_once_with()
    config.reset_output_device.assert_called_once_with()