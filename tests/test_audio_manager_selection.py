from __future__ import annotations

from jarvis.audio.manager import AudioManager


class FakeSoundDevice:
    @staticmethod
    def query_hostapis():
        return (
            {"name": "Windows WASAPI"},
            {"name": "MME"},
        )

    @staticmethod
    def query_devices():
        return (
            {
                "name": "Stereo Mix",
                "hostapi": 0,
                "max_input_channels": 2,
                "max_output_channels": 0,
                "default_samplerate": 48000.0,
            },
            {
                "name": "USB Microphone",
                "hostapi": 0,
                "max_input_channels": 1,
                "max_output_channels": 0,
                "default_samplerate": 48000.0,
            },
            {
                "name": "Speakers Realtek",
                "hostapi": 0,
                "max_input_channels": 0,
                "max_output_channels": 2,
                "default_samplerate": 48000.0,
            },
            {
                "name": "Backup Speaker",
                "hostapi": 1,
                "max_input_channels": 0,
                "max_output_channels": 2,
                "default_samplerate": 44100.0,
            },
        )


def test_manager_auto_selects_usable_devices() -> None:
    manager = AudioManager(
        sounddevice_module=FakeSoundDevice(),
    )

    assert manager.input_device == 1
    assert manager.output_device == 2


def test_manager_supports_explicit_device_selection() -> None:
    manager = AudioManager(
        sounddevice_module=FakeSoundDevice(),
        input_device=1,
        output_device=3,
    )

    assert manager.input_device == 1
    assert manager.output_device == 3


def test_manager_can_change_output_at_runtime() -> None:
    manager = AudioManager(
        sounddevice_module=FakeSoundDevice(),
    )

    selected = manager.select_output(3)

    assert selected.index == 3
    assert manager.output_device == 3


def test_manager_lists_input_and_output_devices() -> None:
    manager = AudioManager(
        sounddevice_module=FakeSoundDevice(),
    )

    assert tuple(
        item.index
        for item in manager.input_devices()
    ) == (0, 1)

    assert tuple(
        item.index
        for item in manager.output_devices()
    ) == (2, 3)
