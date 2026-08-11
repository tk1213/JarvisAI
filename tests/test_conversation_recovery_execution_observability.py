from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.conversation.reliability import ConversationFallbackKind
from jarvis.services.conversation_manager import ConversationManager


def build_manager(
    *,
    timeout_seconds: float = 1.0,
) -> ConversationManager:
    memory = Mock()
    memory.save_message = AsyncMock()
    memory.get_ai_history = AsyncMock(
        return_value=[]
    )

    return ConversationManager(
        ai=Mock(),
        memory=memory,
        router=Mock(),
        conversation_timeout_seconds=timeout_seconds,
    )


@pytest.mark.asyncio
async def test_timeout_recovery_is_attached_to_last_turn() -> None:
    manager = build_manager(
        timeout_seconds=0.01
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
        "slow"
    )

    assert reply == manager.recovery_safe_message

    execution = manager.last_recovery_execution

    assert execution is not None
    assert execution.executed is True
    assert execution.fallback_kind is ConversationFallbackKind.SAFE_MESSAGE
    assert execution.attempts_used == 1


@pytest.mark.asyncio
async def test_recovery_execution_is_preserved_in_turn_history() -> None:
    manager = build_manager(
        timeout_seconds=0.01
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

    await manager.ask(
        "slow"
    )

    history = manager._turn_lifecycle.list_recent(  # type: ignore[attr-defined]
        limit=1
    )

    assert len(history) == 1
    assert history[0].recovery_execution is not None


@pytest.mark.asyncio
async def test_successful_turn_has_no_recovery_execution() -> None:
    manager = build_manager()

    manager._ask_legacy = AsyncMock(  # type: ignore[method-assign]
        return_value="ok"
    )

    await manager.ask(
        "hello"
    )

    assert manager.last_recovery_execution is None
