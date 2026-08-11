from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.services.conversation_manager import ConversationManager


@pytest.mark.asyncio
async def test_retryable_timeout_returns_safe_message_instead_of_reraising() -> None:
    memory = Mock()
    memory.save_message = AsyncMock()
    memory.get_ai_history = AsyncMock(
        return_value=[]
    )

    manager = ConversationManager(
        ai=Mock(),
        memory=memory,
        router=Mock(),
        conversation_timeout_seconds=0.01,
    )

    async def slow(
        text: str,
    ) -> str:
        del text
        await asyncio.sleep(1)
        return "late"

    manager._ask_legacy = slow  # type: ignore[method-assign]

    reply = await manager.ask(
        "slow"
    )

    assert reply == manager.recovery_safe_message
