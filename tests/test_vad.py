from __future__ import annotations

import numpy as np
import pytest

from jarvis.audio.vad import (
    VoiceActivityDetector,
)


def make_pcm_frame(
    amplitude: int,
    samples: int = 320,
) -> bytes:
    data = np.full(
        samples,
        amplitude,
        dtype=np.int16,
    )

    return data.tobytes()


def test_empty_frame_is_not_speech() -> None:
    vad = VoiceActivityDetector(
        threshold=500.0
    )

    result = vad.analyze(
        b""
    )

    assert not result.is_speech
    assert result.rms == 0.0


def test_silence_is_not_speech() -> None:
    vad = VoiceActivityDetector(
        threshold=500.0
    )

    frame = make_pcm_frame(
        amplitude=0
    )

    result = vad.analyze(
        frame
    )

    assert not result.is_speech
    assert result.rms == 0.0


def test_low_level_noise_is_not_speech() -> None:
    vad = VoiceActivityDetector(
        threshold=500.0
    )

    frame = make_pcm_frame(
        amplitude=100
    )

    result = vad.analyze(
        frame
    )

    assert not result.is_speech
    assert result.rms == pytest.approx(
        100.0
    )


def test_loud_frame_is_speech() -> None:
    vad = VoiceActivityDetector(
        threshold=500.0
    )

    frame = make_pcm_frame(
        amplitude=2000
    )

    result = vad.analyze(
        frame
    )

    assert result.is_speech
    assert result.rms == pytest.approx(
        2000.0
    )


def test_is_speech_shortcut() -> None:
    vad = VoiceActivityDetector(
        threshold=500.0
    )

    speech_frame = make_pcm_frame(
        amplitude=1500
    )

    silence_frame = make_pcm_frame(
        amplitude=50
    )

    assert vad.is_speech(
        speech_frame
    )

    assert not vad.is_speech(
        silence_frame
    )


def test_invalid_threshold() -> None:
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        VoiceActivityDetector(
            threshold=0.0
        )