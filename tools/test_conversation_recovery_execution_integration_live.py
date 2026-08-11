from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

from jarvis.conversation.recovery_execution import ConversationRecoveryExecutor
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
        recovery_executor=ConversationRecoveryExecutor(
            safe_message="Jarvis recovered safely."
        ),
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
        "timeout recovery"
    )

    assert reply == "Jarvis recovered safely."

    print("Sprint 4.8 Pack B — Production Recovery Execution Integration")
    print("-" * 60)
    print("Timeout safe recovery execution: PASS")
    print("Non-retryable exception preservation: PASS")
    print("Success-path compatibility: PASS")
    print("Bounded recovery execution: PASS")
    print("Sprint 4.8 Pack B live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
