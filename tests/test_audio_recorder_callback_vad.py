from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import ClassVar

import numpy as np
import pytest

from jarvis.audio.manager import AudioManager
from jarvis.audio.recorder import AudioRecorder


class FakeCallbackStream:
    def __init__(
        self,
        *,
        callback,
        frames,
    ) -> None:
        self._callback = callback
        self._frames = tuple(
            frames
        )

    def __enter__(
        self,
    ):
        for frame in self._frames:
            self._callback(
                frame,
                frame.shape[0],
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
                "default_samplerate": 48000.0,
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

        return FakeCallbackStream(
            callback=callback,
            frames=frames,
        )


def frame(
    level: float,
    frames: int = 960,
) -> np.ndarray:
    return np.full(
        (
            frames,
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


def test_callback_calibration_uses_audio_frames() -> None:
    recorder = build_recorder(
        (
            [frame(0.01)] * 25,
        )
    )

    result = recorder.calibrate_noise(
        calibration_ms=500,
        minimum_threshold=0.005,
        minimum_margin=0.001,
    )

    assert result.noise_rms == pytest.approx(
        0.01
    )
    assert result.threshold > result.noise_rms


def test_callback_vad_records_triggered_speech(
    tmp_path: Path,
) -> None:
    recorder = build_recorder(
        (
            (
                [frame(0.001)] * 3
                + [frame(0.03)] * 8
                + [frame(0.001)] * 50
            ),
        )
    )

    result = recorder.record_until_silence(
        output=tmp_path / "vad.wav",
        threshold=0.005,
        speech_trigger_ms=60,
        silence_duration_ms=100,
        pre_roll_ms=40,
        max_wait_seconds=1.0,
        max_record_seconds=2.0,
        adaptive=False,
    )

    assert result is not None
    assert result.path.exists()

    run = recorder.last_vad_run

    assert run is not None
    assert run.triggered is True
    assert run.trigger_rms is not None
    assert run.trigger_rms > run.threshold


def test_callback_vad_rejects_silence() -> None:
    recorder = build_recorder(
        (
            [frame(0.001)] * 30,
        )
    )

    result = recorder.record_until_silence(
        threshold=0.005,
        max_wait_seconds=0.1,
        adaptive=False,
    )

    assert result is None

    run = recorder.last_vad_run

    assert run is not None
    assert run.triggered is False

def test_callback_vad_can_be_cancelled_cooperatively() -> None:
    recorder = build_recorder(
        (
            (),
        )
    )

    cancel_event = threading.Event()
    result_holder: list[object] = []

    def capture() -> None:
        result_holder.append(
            recorder.record_until_silence(
                threshold=0.005,
                max_wait_seconds=10.0,
                adaptive=False,
                cancel_event=cancel_event,
            )
        )

    worker = threading.Thread(
        target=capture,
    )

    worker.start()

    time.sleep(0.05)
    cancel_event.set()

    worker.join(
        timeout=1.0,
    )

    assert worker.is_alive() is False
    assert result_holder == [None]

def test_callback_calibration_can_be_cancelled_cooperatively() -> None:
    recorder = build_recorder(
        (
            (),
        )
    )

    cancel_event = threading.Event()
    result_holder: list[object] = []

    def calibrate() -> None:
        result_holder.append(
            recorder.calibrate_noise(
                calibration_ms=500,
                cancel_event=cancel_event,
            )
        )

    worker = threading.Thread(
        target=calibrate,
    )

    worker.start()

    time.sleep(0.05)
    cancel_event.set()

    worker.join(
        timeout=1.0,
    )

    assert worker.is_alive() is False
    assert result_holder == [None]