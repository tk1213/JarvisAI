from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pytest

from jarvis.audio.manager import AudioManager
from jarvis.audio.player import AudioPlayer


def test_playback_start_is_not_reported_when_dispatch_fails(
    tmp_path: Path,
) -> None:
    audio_file = tmp_path / "reply.wav"
    audio_file.touch()

    audio = Mock(
        spec=AudioManager
    )
    audio.output_device = 7

    player = AudioPlayer(
        audio=audio
    )

    on_playback_start = Mock()

    samples = np.zeros(
        160,
        dtype=np.float32,
    )

    output_info = {
        "name": "Fake Output",
        "default_samplerate": 16000,
        "max_output_channels": 2,
    }

    with (
        patch(
            "jarvis.audio.player.sf.read",
            return_value=(
                samples,
                16000,
            ),
        ),
        patch(
            "jarvis.audio.player.sd.query_devices",
            return_value=output_info,
        ),
        patch(
            "jarvis.audio.player.sd.check_output_settings",
        ),
        patch(
            "jarvis.audio.player.sd.play",
            side_effect=RuntimeError(
                "playback dispatch failed"
            ),
        ),
        pytest.raises(
            RuntimeError,
            match="playback dispatch failed",
        ),
    ):
        player.play(
            audio_file,
            on_playback_start=on_playback_start,
        )

    on_playback_start.assert_not_called()

def test_blocking_play_reports_start_before_waiting_for_completion(
    tmp_path: Path,
) -> None:
    audio_file = tmp_path / "reply.wav"
    audio_file.touch()

    audio = Mock(
        spec=AudioManager
    )
    audio.output_device = 7

    player = AudioPlayer(
        audio=audio
    )

    samples = np.zeros(
        160,
        dtype=np.float32,
    )

    output_info = {
        "name": "Fake Output",
        "default_samplerate": 16000,
        "max_output_channels": 2,
    }

    events: list[str] = []

    def mark_start() -> None:
        events.append("start")

    def wait() -> None:
        events.append("wait")

    with (
        patch(
            "jarvis.audio.player.sf.read",
            return_value=(
                samples,
                16000,
            ),
        ),
        patch(
            "jarvis.audio.player.sd.query_devices",
            return_value=output_info,
        ),
        patch(
            "jarvis.audio.player.sd.check_output_settings",
        ),
        patch(
            "jarvis.audio.player.sd.play",
        ) as play,
        patch(
            "jarvis.audio.player.sd.wait",
            side_effect=wait,
        ),
    ):
        player.play(
            audio_file,
            on_playback_start=mark_start,
        )

    play.assert_called_once()

    assert (
        play.call_args.kwargs["blocking"]
        is False
    )

    assert events == [
        "start",
        "wait",
    ]