from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from jarvis.audio.signal_diagnostics import (
    AudioSignalAnalyzer,
    AudioSignalStatus,
)


def write_audio(
    path: Path,
    data: np.ndarray,
    *,
    sample_rate: int = 16000,
) -> None:
    sf.write(
        path,
        data.astype(
            np.float32
        ),
        sample_rate,
    )


def test_silent_audio_is_detected(
    tmp_path: Path,
) -> None:
    path = tmp_path / "silent.wav"

    write_audio(
        path,
        np.zeros(
            1600,
            dtype=np.float32,
        ),
    )

    result = AudioSignalAnalyzer().analyze(
        path
    )

    assert result.status is AudioSignalStatus.SILENT
    assert result.rms == pytest.approx(
        0.0
    )
    assert result.peak == pytest.approx(
        0.0
    )
    assert result.usable_for_stt is False


def test_low_audio_is_detected(
    tmp_path: Path,
) -> None:
    path = tmp_path / "low.wav"

    write_audio(
        path,
        np.full(
            1600,
            0.01,
            dtype=np.float32,
        ),
    )

    result = AudioSignalAnalyzer().analyze(
        path
    )

    assert result.status is AudioSignalStatus.LOW
    assert result.usable_for_stt is True


def test_normal_audio_is_detected(
    tmp_path: Path,
) -> None:
    path = tmp_path / "normal.wav"

    samples = np.sin(
        np.linspace(
            0,
            30,
            1600,
            dtype=np.float32,
        )
    ) * 0.1

    write_audio(
        path,
        samples,
    )

    result = AudioSignalAnalyzer().analyze(
        path
    )

    assert result.status is AudioSignalStatus.NORMAL
    assert result.usable_for_stt is True


def test_clipping_is_detected(
    tmp_path: Path,
) -> None:
    path = tmp_path / "clip.wav"

    write_audio(
        path,
        np.full(
            1600,
            0.99,
            dtype=np.float32,
        ),
    )

    result = AudioSignalAnalyzer().analyze(
        path
    )

    assert result.status is AudioSignalStatus.CLIPPING
    assert result.usable_for_stt is False


def test_invalid_threshold_configuration_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="low_rms_threshold",
    ):
        AudioSignalAnalyzer(
            silence_rms_threshold=0.02,
            low_rms_threshold=0.01,
        )
