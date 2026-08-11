from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.stt_service import STTService
from jarvis.services.tts_service import TTSService


class VoiceTurnStatus(StrEnum):
    COMPLETED = "completed"
    NO_SPEECH = "no_speech"
    NO_REPLY = "no_reply"


@dataclass(slots=True, frozen=True)
class VoiceTurnResult:
    status: VoiceTurnStatus
    transcript: str
    reply: str

    @property
    def completed(self) -> bool:
        return self.status is VoiceTurnStatus.COMPLETED


class VoiceTurnRuntime:
    """One production voice turn: VAD -> STT -> conversation -> TTS."""

    def __init__(
        self,
        *,
        stt: STTService,
        conversation: ConversationManager,
        tts: TTSService,
    ) -> None:
        self._stt = stt
        self._conversation = conversation
        self._tts = tts

    async def run(
        self,
        *,
        language: str = "th",
    ) -> VoiceTurnResult:
        transcript = (
            await self._stt.listen_vad(
                language=language,
            )
        ).strip()

        if not transcript:
            return VoiceTurnResult(
                status=VoiceTurnStatus.NO_SPEECH,
                transcript="",
                reply="",
            )

        reply = (
            await self._conversation.ask(
                transcript
            )
        ).strip()

        if not reply:
            return VoiceTurnResult(
                status=VoiceTurnStatus.NO_REPLY,
                transcript=transcript,
                reply="",
            )

        await self._tts.speak(
            reply
        )

        return VoiceTurnResult(
            status=VoiceTurnStatus.COMPLETED,
            transcript=transcript,
            reply=reply,
        )
