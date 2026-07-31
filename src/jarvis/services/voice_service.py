from __future__ import annotations

from jarvis.core.session import SessionState
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.session_manager import SessionManager
from jarvis.services.stt_service import STTService
from jarvis.services.tts_service import TTSService


class VoiceService:
    def __init__(
        self,
        stt: STTService,
        conversation: ConversationManager,
        tts: TTSService,
        session: SessionManager,
    ) -> None:
        self._stt = stt
        self._conversation = conversation
        self._tts = tts
        self._session = session

    async def listen_and_reply(
        self,
        seconds: float = 5.0,
        language: str = "th",
    ) -> str:
        try:
            await self._session.set_state(
                SessionState.LISTENING,
            )

            text = await self._stt.listen(
                seconds=seconds,
                language=language,
            )

            text = text.strip()

            if not text:
                print("\n[No speech detected]")
                return ""

            print(f"\n🎤 You : {text}")

            await self._session.set_state(
                SessionState.THINKING,
            )

            reply = await self._conversation.ask(
                text=text,
            )

            reply = reply.strip()

            if not reply:
                print("\n[AI returned no response]")
                return ""

            print(f"\n🤖 Jarvis : {reply}")

            await self._session.set_state(
                SessionState.SPEAKING,
            )

            await self._tts.speak(
                text=reply,
            )

            return reply

        finally:
            await self._session.set_state(
                SessionState.IDLE,
            )