from __future__ import annotations

from unittest.mock import Mock, patch

from jarvis.core.service_factory import ServiceFactory
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.session_manager import SessionManager


def main() -> None:
    container = Mock()

    conversation = Mock(spec=ConversationManager)
    session = Mock(spec=SessionManager)

    def resolve(
        name: str,
        expected_type=None,
    ):
        del expected_type

        if name == "conversation":
            return conversation

        if name == "session":
            return session

        raise AssertionError(name)

    container.resolve.side_effect = resolve

    with (
        patch(
            "jarvis.core.service_factory.AudioManager"
        ) as audio_type,
        patch(
            "jarvis.core.service_factory.SpeechToText"
        ),
        patch(
            "jarvis.core.service_factory.TextToSpeech"
        ),
        patch(
            "jarvis.core.service_factory.WakeWordService"
        ) as wake_type,
        patch(
            "jarvis.core.service_factory.AssistantRuntimeService"
        ),
        patch(
            "jarvis.core.service_factory.VoiceService"
        ),
    ):
        audio = audio_type.return_value

        ServiceFactory(container).register_voice()

        wake_type.assert_called_once_with(
            audio=audio
        )

    names = [
        call.args[0]
        for call in container.register.call_args_list
    ]

    assert "audio" in names
    assert "wake_word" in names
    assert "wake_activation" in names
    assert "assistant_runtime" in names

    print("Sprint 6 Pack C — Production Wake Wiring")
    print("-" * 60)
    print("Shared AudioManager wiring: PASS")
    print("WakeWordService wiring: PASS")
    print("WakeActivationBoundary registration: PASS")
    print("Assistant runtime registration: PASS")
    print("Sprint 6 Pack C live gate: PASS")


if __name__ == "__main__":
    main()
