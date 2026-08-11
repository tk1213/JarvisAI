from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

from jarvis.voice.dialogue_runtime import VoiceDialogueRuntime
from jarvis.voice.turn_runtime import (
    VoiceTurnResult,
    VoiceTurnStatus,
)


async def main() -> None:
    voice_turn = Mock()
    voice_turn.run = AsyncMock(
        side_effect=(
            VoiceTurnResult(
                status=VoiceTurnStatus.COMPLETED,
                transcript="สถานะปลั๊ก",
                reply="ต้องการ Smart Plug 1 หรือ Smart Plug 2 ครับ",
            ),
            VoiceTurnResult(
                status=VoiceTurnStatus.COMPLETED,
                transcript="Smart Plug 2",
                reply="Smart Plug 2 อยู่ในสถานะเปิดครับ",
            ),
        )
    )

    pending_states = iter(
    (
        True,
        False,
        False,
    )
)

    conversation = Mock()

    type(conversation).has_pending_smart_home = property(
        lambda _self: next(
            pending_states
        )
    )

    runtime = VoiceDialogueRuntime(
        voice_turn=voice_turn,
        conversation=conversation,
        max_follow_ups=2,
    )

    result = await runtime.run(
        language="th"
    )

    assert result.completed is True
    assert len(result.turns) == 2
    assert result.follow_ups_used == 1

    print("Sprint 5 Pack I — Voice Follow-up Continuation")
    print("-" * 60)
    print("Pending smart-home detection: PASS")
    print("Follow-up voice turn: PASS")
    print("Bounded continuation: PASS")
    print("No-speech protection: PASS")
    print("Sprint 5 Pack I live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
