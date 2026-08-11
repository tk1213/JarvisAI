from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

from jarvis.conversation.reliability import ConversationFailureKind
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
        "diagnostics live"
    )

    snapshot = manager.diagnostics_snapshot

    assert reply == manager.recovery_safe_message
    assert snapshot is not None
    assert snapshot.reliability.failure_kind is ConversationFailureKind.TIMEOUT
    assert snapshot.recovery.executed is True

    print("Sprint 4.9 Pack B — Production Diagnostics Integration")
    print("-" * 60)
    print("ConversationManager diagnostics snapshot: PASS")
    print("Failure diagnostics integration: PASS")
    print("Recovery diagnostics integration: PASS")
    print("Production behavior compatibility: PASS")
    print("Sprint 4.9 Pack B live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
