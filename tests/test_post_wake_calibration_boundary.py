from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import numpy as np
import pytest

from jarvis.audio.manager import AudioManager
from jarvis.audio.recorder import AudioRecorder


class FakeStream:
    def __init__(
        self,
        *,
        frames,
        callback,
    ) -> None:
        self._frames = tuple(frames)
        self._callback = callback

    def __enter__(self):
        for frame in self._frames:
            self._callback(
                frame,
                frame.shape[0],
                object(),
                None,
            )

        return self

    def __exit__(self, *args):
        return False


class FakeSoundDevice:
    stream_batches: ClassVar[list] = []

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
                "name": "Speakers",
                "hostapi": 0,
                "max_input_channels": 0,
                "max_output_channels": 2,
                "default_samplerate": 48000.0,
            },
        )

    @classmethod
    def InputStream(
        cls,
        *,
        callback,
        **kwargs,
    ):
        del kwargs

        frames = cls.stream_batches.pop(
            0
        )

        return FakeStream(
            frames=frames,
            callback=callback,
        )


def frame(
    level: float,
) -> np.ndarray:
    return np.full(
        (
            320,
            1,
        ),
        level,
        dtype=np.float32,
    )


def build_recorder(
    batches,
) -> AudioRecorder:
    FakeSoundDevice.stream_batches = [
        tuple(
            batch
        )
        for batch in batches
    ]

    fake = FakeSoundDevice()

    manager = AudioManager(
        sounddevice_module=fake,
    )

    return AudioRecorder(
        manager,
        sounddevice_module=fake,
    )


def test_calibration_and_capture_use_separate_streams(
    tmp_path: Path,
) -> None:
    recorder = build_recorder(
        (
            [frame(0.012)] * 10,
            (
                [frame(0.012)] * 2
                + [frame(0.025)] * 6
                + [frame(0.012)] * 12
            ),
        )
    )

    calibration = recorder.calibrate_noise(
        calibration_ms=200,
        minimum_threshold=0.005,
        minimum_margin=0.001,
    )

    result = recorder.record_until_silence(
        output=tmp_path / "capture.wav",
        threshold=calibration.threshold,
        adaptive=False,
        speech_trigger_ms=60,
        silence_duration_ms=120,
        max_wait_seconds=1,
    )

    assert result is not None
    assert result.path.exists()

    assert calibration.noise_rms == pytest.approx(
        0.012
    )

    assert (
        calibration.threshold
        > calibration.noise_rms
    )

    run = recorder.last_vad_run

    assert run is not None
    assert run.triggered is True
    assert run.trigger_rms is not None

    assert (
        run.trigger_rms
        > calibration.threshold
    )


def test_stable_noise_does_not_trigger_after_calibration() -> None:
    recorder = build_recorder(
        (
            [frame(0.012)] * 10,
            [frame(0.012)] * 50,
        )
    )

    calibration = recorder.calibrate_noise(
        calibration_ms=200,
        minimum_threshold=0.005,
        minimum_margin=0.001,
    )

    result = recorder.record_until_silence(
        threshold=calibration.threshold,
        adaptive=False,
        max_wait_seconds=1,
    )

    assert result is None

    run = recorder.last_vad_run

    assert run is not None
    assert run.triggered is False

    assert (
        run.max_wait_rms
        < calibration.threshold
    )