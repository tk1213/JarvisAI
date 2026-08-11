from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

from jarvis.conversation.turn import ConversationTurnStatus
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
    )

    legacy = AsyncMock(
        return_value="Jarvis turn integration ready."
    )
    manager._ask_legacy = legacy  # type: ignore[method-assign]

    reply = await manager.ask(
        "hello jarvis"
    )

    assert reply == "Jarvis turn integration ready."
    legacy.assert_awaited_once_with(
        "hello jarvis"
    )
    assert manager.last_turn is not None
    assert manager.last_turn.status is ConversationTurnStatus.COMPLETED

    print("Sprint 4.5 Pack B Hotfix — ConversationManager Integration")
    print("-" * 60)
    print("Wrapper installation: PASS")
    print("Legacy routing delegation: PASS")
    print("Turn lifecycle recording: PASS")
    print("Sprint 4.5 Pack B hotfix live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
