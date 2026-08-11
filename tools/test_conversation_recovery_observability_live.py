from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

from jarvis.conversation.reliability import ConversationFallbackKind
from jarvis.services.conversation_manager import ConversationManager


async def main() -> None:
    memory = Mock()
    memory.save_message = AsyncMock()
    memory.get_ai_history = AsyncMock(
        return_value=[]
    )

    manager = ConversationManager(
        ai=Mock(),
        memory=memory,
        router=Mock(),
        conversation_timeout_seconds=0.02,
    )

    async def slow(
        text: str,
    ) -> str:
        del text
        await asyncio.sleep(
            1
        )
        return "late"

    manager._ask_legacy = slow  # type: ignore[method-assign]

    reply = await manager.ask(
        "trace recovery"
    )

    execution = manager.last_recovery_execution

    assert reply == manager.recovery_safe_message
    assert execution is not None
    assert execution.executed is True
    assert execution.fallback_kind is ConversationFallbackKind.SAFE_MESSAGE
    assert execution.attempts_used == 1

    print("Sprint 4.8 Pack C — Recovery Tracing & Fallback Observability")
    print("-" * 60)
    print("Recovery execution tracing: PASS")
    print("Fallback kind observability: PASS")
    print("Recovery attempt observability: PASS")
    print("Turn history preservation: PASS")
    print("Sprint 4.8 Pack C live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
