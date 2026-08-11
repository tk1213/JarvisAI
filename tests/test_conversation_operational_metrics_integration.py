from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.conversation.reliability import ConversationFailureKind
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
async def test_successful_turn_updates_operational_metrics() -> None:
    manager = build_manager()

    manager._ask_legacy = AsyncMock(  # type: ignore[method-assign]
        return_value="ok"
    )

    await manager.ask(
        "hello"
    )

    snapshot = manager.operational_snapshot

    assert snapshot.total_turns == 1
    assert snapshot.completed_turns == 1
    assert snapshot.failed_turns == 0


@pytest.mark.asyncio
async def test_recovered_timeout_updates_operational_metrics() -> None:
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

    snapshot = manager.operational_snapshot

    assert snapshot.total_turns == 1
    assert snapshot.failed_turns == 1
    assert snapshot.recovered_turns == 1
    assert snapshot.timeout_failures == 1
    assert snapshot.last_failure_kind is ConversationFailureKind.TIMEOUT
