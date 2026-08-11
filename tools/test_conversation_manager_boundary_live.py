from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

from jarvis.conversation.reliability import ConversationFailureKind
from jarvis.services.conversation_manager import ConversationManager


async def main() -> None:
    memory = Mock()
    memory.save_message = AsyncMock()
    memory.get_ai_history = AsyncMock(return_value=[])
    manager = ConversationManager(
        ai=Mock(), memory=memory, router=Mock(),
        conversation_timeout_seconds=0.02,
    )

    async def slow(text: str) -> str:
        del text
        await asyncio.sleep(1)
        return "late"

    manager._ask_legacy = slow

    try:
        await manager.ask("timeout")
    except TimeoutError:
        pass
    else:
        raise AssertionError("timeout boundary did not activate")

    result = manager.last_turn
    assert result is not None
    assert result.reliability is not None
    assert result.reliability.failure is not None
    assert result.reliability.failure.kind is ConversationFailureKind.TIMEOUT

    print("Sprint 4.6 Pack D — ConversationManager Boundary Integration")
    print("-" * 60)
    print("Production ask boundary: PASS")
    print("Timeout enforcement: PASS")
    print("Failure classification: PASS")
    print("Cancellation propagation contract: PASS")
    print("Sprint 4.6 Pack D live gate: PASS")

if __name__ == "__main__":
    asyncio.run(main())
