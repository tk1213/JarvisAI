from __future__ import annotations

from dataclasses import dataclass

from jarvis.services.conversation_manager import ConversationManager
from jarvis.voice.turn_runtime import (
    VoiceTurnResult,
    VoiceTurnRuntime,
    VoiceTurnStatus,
)


@dataclass(slots=True, frozen=True)
class VoiceDialogueResult:
    turns: tuple[VoiceTurnResult, ...]
    pending_smart_home: bool
    follow_ups_used: int

    @property
    def completed(self) -> bool:
        return (
            bool(self.turns)
            and self.turns[-1].status
            is VoiceTurnStatus.COMPLETED
            and not self.pending_smart_home
        )


class VoiceDialogueRuntime:
    """Run one voice turn plus bounded smart-home follow-up turns."""

    def __init__(
        self,
        *,
        voice_turn: VoiceTurnRuntime,
        conversation: ConversationManager,
        max_follow_ups: int = 2,
    ) -> None:
        if max_follow_ups < 0:
            raise ValueError(
                "max_follow_ups cannot be negative."
            )

        self._voice_turn = voice_turn
        self._conversation = conversation
        self._max_follow_ups = max_follow_ups

    @property
    def max_follow_ups(self) -> int:
        return self._max_follow_ups

    async def run(
        self,
        *,
        language: str = "th",
    ) -> VoiceDialogueResult:
        turns: list[VoiceTurnResult] = []
        follow_ups_used = 0

        first = await self._voice_turn.run(
            language=language,
        )
        turns.append(
            first
        )

        if first.status is not VoiceTurnStatus.COMPLETED:
            return VoiceDialogueResult(
                turns=tuple(
                    turns
                ),
                pending_smart_home=(
                    self._conversation.has_pending_smart_home
                ),
                follow_ups_used=0,
            )

        while (
            self._conversation.has_pending_smart_home
            and follow_ups_used < self._max_follow_ups
        ):
            follow_up = await self._voice_turn.run(
                language=language,
            )
            turns.append(
                follow_up
            )
            follow_ups_used += 1

            if follow_up.status is not VoiceTurnStatus.COMPLETED:
                break

        return VoiceDialogueResult(
            turns=tuple(
                turns
            ),
            pending_smart_home=(
                self._conversation.has_pending_smart_home
            ),
            follow_ups_used=follow_ups_used,
        )
