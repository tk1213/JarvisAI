from __future__ import annotations

from unittest.mock import Mock, patch

from jarvis.audio.player import AudioPlayer
from jarvis.audio.recorder import AudioRecorder
from jarvis.core.service_factory import ServiceFactory
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.session_manager import SessionManager
from jarvis.voice.turn_runtime import VoiceTurnRuntime


def test_voice_factory_shares_one_audio_manager() -> None:
    container = Mock()

    conversation = Mock(
        spec=ConversationManager
    )
    session = Mock(
        spec=SessionManager
    )

    def resolve(
        name: str,
        expected_type=None,
    ):
        del expected_type

        if name == "conversation":
            return conversation

        if name == "session":
            return session

        raise AssertionError(
            name
        )

    container.resolve.side_effect = resolve

    with (
        patch(
            "jarvis.core.service_factory.AudioManager"
        ) as manager_type,
        patch(
            "jarvis.core.service_factory.SpeechToText"
        ),
        patch(
            "jarvis.core.service_factory.TextToSpeech"
        ),
        patch(
            "jarvis.core.service_factory.WakeWordService"
        ),
        patch(
            "jarvis.core.service_factory.AssistantRuntimeService"
        ),
        patch(
            "jarvis.core.service_factory.VoiceService"
        ),
    ):
        audio = manager_type.return_value

        ServiceFactory(
            container
        ).register_voice()

    registered = {
        call.args[0]: call.args[1]
        for call in container.register.call_args_list
    }

    assert registered["audio"] is audio

    recorder = registered["recorder"]
    player = registered["player"]

    assert isinstance(
        recorder,
        AudioRecorder,
    )
    assert isinstance(
        player,
        AudioPlayer,
    )
    assert recorder._audio is audio
    assert player.audio is audio

    assert isinstance(
        registered["voice_turn"],
        VoiceTurnRuntime,
    )
