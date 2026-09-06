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

class MutableFakeSoundDevice:
    def __init__(self) -> None:
        self.devices = FakeSoundDevice.query_devices()

    @staticmethod
    def query_hostapis():
        return FakeSoundDevice.query_hostapis()

    def query_devices(self):
        return self.devices

def test_failed_refresh_preserves_previous_manager_state() -> None:
    sounddevice = MutableFakeSoundDevice()

    manager = AudioManager(
        sounddevice_module=sounddevice,
    )

    previous_snapshot = manager.snapshot
    previous_inputs = manager.input_devices()
    previous_outputs = manager.output_devices()

    sounddevice.devices = (
        {
            "name": "Stereo Mix",
            "hostapi": 0,
            "max_input_channels": 2,
            "max_output_channels": 0,
            "default_samplerate": 48000.0,
        },
        {
            "name": "Renamed USB Microphone",
            "hostapi": 0,
            "max_input_channels": 1,
            "max_output_channels": 0,
            "default_samplerate": 48000.0,
        },
        {
            "name": "Disconnected Speaker",
            "hostapi": 0,
            "max_input_channels": 0,
            "max_output_channels": 0,
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

    try:
        manager.refresh()
    except ValueError:
        pass
    else:
        raise AssertionError(
            "refresh() should fail when the selected output is unavailable."
        )

    assert manager.snapshot == previous_snapshot
    assert manager.input_devices() == previous_inputs
    assert manager.output_devices() == previous_outputs