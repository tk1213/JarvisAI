from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from jarvis.audio.manager import AudioManager
from jarvis.audio.recorder import AudioRecorder


class FakeSoundDevice:
    @staticmethod
    def query_hostapis():
        return (
            {
                "name": "Windows WASAPI",
            },
        )

    @staticmethod
    def query_devices():
        return (
            {
                "name": "USB Microphone",
                "hostapi": 0,
                "max_input_channels": 1,
                "max_output_channels": 0,
                "default_samplerate": 16000.0,
            },
            {
                "name": "Speakers Realtek",
                "hostapi": 0,
                "max_input_channels": 0,
                "max_output_channels": 2,
                "default_samplerate": 48000.0,
            },
        )

    @staticmethod
    def rec(
        frames: int,
        *,
        samplerate: int,
        channels: int,
        dtype: str,
        device: int,
        blocking: bool,
    ):
        assert samplerate == 16000
        assert channels == 1
        assert dtype == "float32"
        assert device == 0
        assert blocking is True

        return np.zeros(
            (
                frames,
                channels,
            ),
            dtype=np.float32,
        )


def build_recorder() -> AudioRecorder:
    fake = FakeSoundDevice()

    manager = AudioManager(
        sounddevice_module=fake,
    )

    return AudioRecorder(
        manager,
        sounddevice_module=fake,
    )


def test_recorder_uses_selected_input_device(
    tmp_path: Path,
) -> None:
    recorder = build_recorder()

    result = recorder.record(
        tmp_path / "capture.wav",
        seconds=0.25,
    )

    assert result.device_index == 0
    assert result.sample_rate == 16000
    assert result.channels == 1
    assert result.frames == 4000
    assert result.path.exists()


def test_recorder_rejects_invalid_duration(
    tmp_path: Path,
) -> None:
    recorder = build_recorder()

    with pytest.raises(
        ValueError,
        match="seconds",
    ):
        recorder.record(
            tmp_path / "capture.wav",
            seconds=0,
        )


def test_recorder_rejects_unsupported_channel_count(
    tmp_path: Path,
) -> None:
    recorder = build_recorder()

    with pytest.raises(
        ValueError,
        match="supports only",
    ):
        recorder.record(
            tmp_path / "capture.wav",
            channels=2,
        )


def test_recording_result_duration_is_correct(
    tmp_path: Path,
) -> None:
    recorder = build_recorder()

    result = recorder.record(
        tmp_path / "capture.wav",
        seconds=0.5,
    )

    assert result.duration_seconds == pytest.approx(
        0.5
    )
    assert result.empty is False
