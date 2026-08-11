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
    frames: ClassVar[list] = []

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

        return FakeStream(
            frames=cls.frames,
            callback=callback,
        )


def build_recorder(
    frames,
) -> AudioRecorder:
    FakeSoundDevice.frames = frames
    fake = FakeSoundDevice()

    manager = AudioManager(
        sounddevice_module=fake,
    )

    return AudioRecorder(
        manager,
        sounddevice_module=fake,
    )


def audio_frame(
    level: float,
    size: int = 320,
) -> np.ndarray:
    return np.full(
        (
            size,
            1,
        ),
        level,
        dtype=np.float32,
    )


def test_vad_returns_none_when_no_speech() -> None:
    recorder = build_recorder(
        [audio_frame(0.0)] * 5
    )

    result = recorder.record_until_silence(
        threshold=0.01,
        max_wait_seconds=0.1,
        vad_frame_duration_ms=20,
        adaptive=False,
    )

    assert result is None


def test_vad_records_after_speech_trigger(
    tmp_path: Path,
) -> None:
    frames = (
        [audio_frame(0.0)] * 2
        + [audio_frame(0.1)] * 3
        + [audio_frame(0.0)] * 3
    )

    recorder = build_recorder(
        frames
    )

    result = recorder.record_until_silence(
        output=tmp_path / "vad.wav",
        threshold=0.01,
        speech_trigger_ms=40,
        silence_duration_ms=40,
        pre_roll_ms=20,
        max_wait_seconds=1,
        max_record_seconds=2,
        adaptive=False,
    )

    assert result is not None
    assert result.path.exists()
    assert result.frames > 0