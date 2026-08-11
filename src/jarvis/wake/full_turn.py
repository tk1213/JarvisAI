from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.tts_service import TTSService
from jarvis.wake.command_transition import (
    WakeCommandTransition,
    WakeCommandTransitionResult,
)
from jarvis.wake.timing import TurnTiming


class WakeActivatedTurnStage(StrEnum):
    TRANSITION = "transition"
    CONVERSATION = "conversation"
    TTS_REPLY = "tts_reply"
    COMPLETED = "completed"


@dataclass(slots=True, frozen=True)
class WakeActivatedTurnResult:
    wake_score: float
    transcript: str
    reply: str
    timing: TurnTiming | None = None

    @property
    def completed(self) -> bool:
        return bool(
            self.transcript.strip()
            and self.reply.strip()
        )


class WakeActivatedTurnRuntime:
    """Run one bounded wake-activated Jarvis conversation turn."""

    def __init__(
        self,
        *,
        transition: WakeCommandTransition,
        conversation: ConversationManager,
        tts: TTSService,
    ) -> None:
        self._transition = transition
        self._conversation = conversation
        self._tts = tts
        self._stage = WakeActivatedTurnStage.TRANSITION

    @property
    def stage(self) -> WakeActivatedTurnStage:
        return self._stage

    @property
    def transition(self) -> WakeCommandTransition:
        return self._transition

    async def run(
        self,
        *,
        language: str = "th",
    ) -> WakeActivatedTurnResult:
        self._stage = WakeActivatedTurnStage.TRANSITION

        transition_result = await self._transition.run(
            language=language,
        )

        return await self._complete_transition(
            transition_result
        )

    async def _complete_transition(
        self,
        transition_result: WakeCommandTransitionResult,
    ) -> WakeActivatedTurnResult:
        transcript = transition_result.transcript.strip()
        timing = transition_result.timing

        if not transcript:
            self._stage = WakeActivatedTurnStage.COMPLETED

            return WakeActivatedTurnResult(
                wake_score=transition_result.wake_score,
                transcript="",
                reply="",
                timing=timing,
            )

        self._stage = WakeActivatedTurnStage.CONVERSATION

        reply = (
            await self._conversation.ask(
                transcript,
                voice_mode=True,
            )
        ).strip()

        if timing is not None:
            timing.mark_conversation_done()

        if reply:
            self._stage = WakeActivatedTurnStage.TTS_REPLY

            await self._tts.speak(
                text=reply,
                output="wake_turn_reply.wav",
            )

        if timing is not None:
            timing.mark_tts_done()

        self._stage = WakeActivatedTurnStage.COMPLETED

        return WakeActivatedTurnResult(
            wake_score=transition_result.wake_score,
            transcript=transcript,
            reply=reply,
            timing=timing,
        )