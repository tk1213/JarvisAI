from __future__ import annotations

import asyncio
import threading
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.services.tts_service import TTSService


@pytest.mark.asyncio
async def test_speak_runs_blocking_player_off_event_loop(
    tmp_path: Path,
) -> None:
    audio_file = tmp_path / "reply.wav"
    audio_file.touch()

    event_loop_thread = threading.get_ident()
    playback_thread: int | None = None

    player = Mock()

    def play(
        filename: str | Path,
        *,
        on_playback_start,
    ) -> None:
        nonlocal playback_thread

        del filename

        playback_thread = threading.get_ident()
        on_playback_start()

    player.play.side_effect = play

    tts = Mock()
    tts.generate = AsyncMock(
        return_value=audio_file,
    )

    service = TTSService(
        player=player,
        tts=tts,
    )

    result = await service.speak(
        "hello",
        output=str(audio_file),
    )

    assert result == audio_file
    assert playback_thread is not None
    assert playback_thread != event_loop_thread

@pytest.mark.asyncio
async def test_speak_cancellation_stops_playback_and_waits_for_worker(
    tmp_path: Path,
) -> None:
    audio_file = tmp_path / "reply.wav"
    audio_file.touch()

    playback_started = threading.Event()
    playback_stopped = threading.Event()
    playback_finished = threading.Event()

    player = Mock()

    def play(
        filename: str | Path,
        *,
        on_playback_start,
    ) -> None:
        del filename

        on_playback_start()
        playback_started.set()

        playback_stopped.wait(
            timeout=5.0,
        )

        playback_finished.set()

    player.play.side_effect = play

    def stop() -> None:
        playback_stopped.set()

    player.stop.side_effect = stop

    tts = Mock()
    tts.generate = AsyncMock(
        return_value=audio_file,
    )

    service = TTSService(
        player=player,
        tts=tts,
    )

    task = asyncio.create_task(
        service.speak(
            "hello",
            output=str(audio_file),
        )
    )

    started = await asyncio.to_thread(
        playback_started.wait,
        1.0,
    )

    assert started is True

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await task

    player.stop.assert_called_once()
    assert playback_finished.is_set()

@pytest.mark.asyncio
async def test_speak_cancellation_during_generation_does_not_stop_player(
    tmp_path: Path,
) -> None:
    audio_file = tmp_path / "reply.wav"

    generation_started = asyncio.Event()

    async def blocked_generate(
        *,
        text: str,
        output: str,
    ) -> Path:
        del text
        del output

        generation_started.set()
        await asyncio.Future()

        return audio_file

    tts = Mock()
    tts.generate = AsyncMock(
        side_effect=blocked_generate,
    )

    player = Mock()

    service = TTSService(
        player=player,
        tts=tts,
    )

    task = asyncio.create_task(
        service.speak(
            "hello",
            output=str(audio_file),
        )
    )

    await generation_started.wait()

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await task

    player.play.assert_not_called()
    player.stop.assert_not_called()