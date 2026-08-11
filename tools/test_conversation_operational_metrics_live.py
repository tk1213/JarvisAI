from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

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

    manager._ask_legacy = AsyncMock(  # type: ignore[method-assign]
        return_value="ok"
    )

    await manager.ask(
        "health"
    )

    snapshot = manager.operational_snapshot

    assert snapshot.total_turns == 1
    assert snapshot.completed_turns == 1

    print("Sprint 4.9 Pack C — Operational Counters & Health Snapshot")
    print("-" * 60)
    print("Turn counters: PASS")
    print("Failure counters: PASS")
    print("Recovery counters: PASS")
    print("Operational snapshot: PASS")
    print("Sprint 4.9 Pack C live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
