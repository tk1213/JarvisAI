from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import numpy as np

from jarvis.audio.manager import AudioManager
from jarvis.audio.recorder import AudioRecorder


class FakeStream:
    def __init__(
        self,
        *,
        frames,
        callback,
    ) -> None:
        self._frames = tuple(
            frames
        )
        self._callback = callback

    def __enter__(
        self,
    ):
        for audio_frame in self._frames:
            self._callback(
                audio_frame,
                audio_frame.shape[0],
                object(),
                None,
            )

        return self

    def __exit__(
        self,
        *args,
    ):
        return False


class FakeSoundDevice:
    stream_batches: ClassVar[
        list[tuple[np.ndarray, ...]]
    ] = []

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


def recorder_with(
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


def test_adaptive_vad_rejects_stable_noise() -> None:
    recorder = recorder_with(
        (
            [frame(0.012)] * 10,
            [frame(0.012)] * 50,
        )
    )

    result = recorder.record_until_silence(
        threshold=0.005,
        adaptive=True,
        calibration_ms=200,
        max_wait_seconds=1.0,
    )

    assert result is None

    calibration = recorder.last_vad_calibration

    assert calibration is not None
    assert calibration.noise_rms > 0.01
    assert (
        calibration.threshold
        > calibration.noise_rms
    )

    run = recorder.last_vad_run

    assert run is not None
    assert run.triggered is False


def test_adaptive_vad_detects_signal_above_noise(
    tmp_path: Path,
) -> None:
    recorder = recorder_with(
        (
            [frame(0.012)] * 10,
            (
                [frame(0.035)] * 6
                + [frame(0.012)] * 50
            ),
        )
    )

    result = recorder.record_until_silence(
        output=tmp_path / "adaptive.wav",
        threshold=0.005,
        adaptive=True,
        calibration_ms=200,
        speech_trigger_ms=60,
        silence_duration_ms=200,
        max_wait_seconds=2.0,
    )

    assert result is not None
    assert result.path.exists()

    calibration = recorder.last_vad_calibration

    assert calibration is not None
    assert calibration.threshold > 0.012
    assert calibration.threshold < 0.035

    run = recorder.last_vad_run

    assert run is not None
    assert run.triggered is True
    assert run.trigger_rms is not None
    assert (
        run.trigger_rms
        > calibration.threshold
    )