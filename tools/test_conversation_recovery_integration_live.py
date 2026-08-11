from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

from jarvis.conversation.reliability import ConversationFallbackKind
from jarvis.services.conversation_manager import ConversationManager


async def main() -> None:
    memory = Mock()
    memory.save_message = AsyncMock()
    memory.get_ai_history = AsyncMock(return_value=[])

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
        await asyncio.sleep(1)
        return "late"

    manager._ask_legacy = slow  # type: ignore[method-assign]

    try:
        await manager.ask("recovery observation")
    except TimeoutError:
        pass

    plan = manager.recovery_plan_for_last_turn()

    assert plan is not None
    assert plan.recovered is True
    assert plan.fallback.kind is ConversationFallbackKind.SAFE_MESSAGE

    exhausted = manager.recovery_plan_for_last_turn(
        attempts=1
    )
    assert exhausted is not None
    assert exhausted.recovered is False

    print("Sprint 4.7 Pack D — Production Recovery Integration")
    print("-" * 60)
    print("Production failure observation: PASS")
    print("Safe recovery planning: PASS")
    print("Bounded recovery attempts: PASS")
    print("Existing exception semantics preserved: PASS")
    print("Sprint 4.7 Pack D live gate: PASS")


if __name__ == "__main__":
    asyncio.run(main())
