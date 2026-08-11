from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.audio.recorder import AudioRecordingResult
from jarvis.audio.signal_diagnostics import (
    AudioSignalDiagnostics,
    AudioSignalStatus,
)
from jarvis.services.stt_service import STTService


def recording(
    path: Path,
) -> AudioRecordingResult:
    return AudioRecordingResult(
        path=path,
        sample_rate=16000,
        channels=1,
        frames=16000,
        duration_seconds=1.0,
        device_index=3,
    )


def diagnostics(
    path: Path,
    *,
    status: AudioSignalStatus,
) -> AudioSignalDiagnostics:
    return AudioSignalDiagnostics(
        path=path,
        sample_rate=16000,
        frames=16000,
        channels=1,
        rms=0.05,
        peak=0.2,
        status=status,
    )


@pytest.mark.asyncio
async def test_listen_fixed_uses_recording_result_path(
    tmp_path: Path,
) -> None:
    path = tmp_path / "record.wav"

    recorder = Mock()
    recorder.record.return_value = recording(
        path
    )

    analyzer = Mock()
    analyzer.analyze.return_value = diagnostics(
        path,
        status=AudioSignalStatus.NORMAL,
    )

    stt = Mock()
    stt.transcribe = AsyncMock(
        return_value=" สวัสดี Jarvis "
    )

    service = STTService(
        recorder=recorder,
        stt=stt,
        signal_analyzer=analyzer,
    )

    text = await service.listen_fixed(
        seconds=1.0,
        language="th",
        output=str(
            path
        ),
    )

    assert text == "สวัสดี Jarvis"

    stt.transcribe.assert_awaited_once_with(
        audio_file=path,
        language="th",
    )


@pytest.mark.asyncio
async def test_silent_recording_is_not_sent_to_stt(
    tmp_path: Path,
) -> None:
    path = tmp_path / "silent.wav"

    recorder = Mock()
    recorder.record.return_value = recording(
        path
    )

    analyzer = Mock()
    analyzer.analyze.return_value = diagnostics(
        path,
        status=AudioSignalStatus.SILENT,
    )

    stt = Mock()
    stt.transcribe = AsyncMock(
        return_value="should not be used"
    )

    service = STTService(
        recorder=recorder,
        stt=stt,
        signal_analyzer=analyzer,
    )

    text = await service.listen_fixed(
        output=str(
            path
        )
    )

    assert text == ""
    stt.transcribe.assert_not_awaited()


@pytest.mark.asyncio
async def test_clipping_recording_is_not_sent_to_stt(
    tmp_path: Path,
) -> None:
    path = tmp_path / "clip.wav"

    recorder = Mock()
    recorder.record.return_value = recording(
        path
    )

    analyzer = Mock()
    analyzer.analyze.return_value = diagnostics(
        path,
        status=AudioSignalStatus.CLIPPING,
    )

    stt = Mock()
    stt.transcribe = AsyncMock()

    service = STTService(
        recorder=recorder,
        stt=stt,
        signal_analyzer=analyzer,
    )

    text = await service.listen_fixed(
        output=str(
            path
        )
    )

    assert text == ""
    stt.transcribe.assert_not_awaited()


@pytest.mark.asyncio
async def test_transcribe_file_can_bypass_signal_validation(
    tmp_path: Path,
) -> None:
    path = tmp_path / "existing.wav"

    recorder = Mock()
    analyzer = Mock()

    stt = Mock()
    stt.transcribe = AsyncMock(
        return_value="hello"
    )

    service = STTService(
        recorder=recorder,
        stt=stt,
        signal_analyzer=analyzer,
    )

    text = await service.transcribe_file(
        path,
        language="en",
        validate_signal=False,
    )

    assert text == "hello"
    analyzer.analyze.assert_not_called()
