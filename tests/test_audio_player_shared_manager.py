from __future__ import annotations

from unittest.mock import Mock, patch

from jarvis.audio.manager import AudioManager
from jarvis.audio.player import AudioPlayer


def test_audio_player_accepts_shared_audio_manager() -> None:
    audio = Mock(
        spec=AudioManager
    )

    player = AudioPlayer(
        audio=audio
    )

    assert player.audio is audio


def test_audio_player_keeps_backward_compatible_default() -> None:
    with patch(
        "jarvis.audio.player.AudioManager"
    ) as manager_type:
        manager = manager_type.return_value

        player = AudioPlayer()

        assert player.audio is manager
        manager_type.assert_called_once_with()
