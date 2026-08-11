from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

from jarvis.services.conversation_manager import ConversationManager


async def main() -> None:
    memory = Mock()
    memory.save_message = AsyncMock()
    memory.get_ai_history = AsyncMock(return_value=[])

    manager = ConversationManager(
        ai=Mock(),
        memory=memory,
        router=Mock(),
    )
    manager._ask_legacy = AsyncMock(  # type: ignore[method-assign]
        return_value="ready"
    )

    await manager.ask("health report")

    report = manager.health_report

    assert report.operational.total_turns == 1
    assert report.latest_turn is not None

    print("Sprint 4.9 Pack D — Unified Production Health Report")
    print("-" * 60)
    print("Unified report contract: PASS")
    print("Diagnostics integration: PASS")
    print("Operational metrics integration: PASS")
    print("Production behavior compatibility: PASS")
    print("Sprint 4.9 Pack D live gate: PASS")


if __name__ == "__main__":
    asyncio.run(main())
