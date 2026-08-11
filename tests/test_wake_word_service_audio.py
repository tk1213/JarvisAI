from __future__ import annotations

from unittest.mock import Mock, patch

from jarvis.audio.manager import AudioManager
from jarvis.services.wake_word_service import WakeWordService


def test_wake_word_accepts_shared_audio_manager() -> None:
    audio = Mock(
        spec=AudioManager
    )

    with (
        patch(
            "jarvis.services.wake_word_service.OpenWakeWordFeatures"
        ) as features_type,
        patch(
            "jarvis.services.wake_word_service.OpenWakeWord"
        ) as wake_type,
    ):
        service = WakeWordService(
            audio=audio
        )

    assert service.audio is audio
    features_type.from_builtin.assert_called_once_with()
    wake_type.from_builtin.assert_called_once()


def test_wake_word_keeps_backward_compatible_audio_default() -> None:
    with (
        patch(
            "jarvis.services.wake_word_service.AudioManager"
        ) as audio_type,
        patch(
            "jarvis.services.wake_word_service.OpenWakeWordFeatures"
        ),
        patch(
            "jarvis.services.wake_word_service.OpenWakeWord"
        ),
    ):
        service = WakeWordService()

    assert service.audio is audio_type.return_value
    audio_type.assert_called_once_with()
